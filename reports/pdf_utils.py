"""Minimal, dependency-free PDF writer for report exports (PDF 1.4, base-14 fonts)."""
import datetime

PAGE_W, PAGE_H = 842, 595
MARGIN_L, MARGIN_R, MARGIN_T = 36, 36, 36
MARGIN_B = 34
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R
BOTTOM = MARGIN_B + 6

_PAD = 4
_CELL_SIZE = 8
_LEADING = 10
_HEADER_SIZE = 8.5
_HEADER_H = 16

# Helvetica AFM widths (1/1000 em), ASCII 32..126
_HELV = (
    278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278,
    556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556,
    1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556,
    333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
    556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584,
)
# Helvetica-Bold AFM widths, ASCII 32..126
_HELV_B = (
    278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278, 278,
    556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 333, 333, 584, 584, 584, 611,
    975, 722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333, 278, 333, 584, 556,
    333, 556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611,
    611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500, 389, 280, 389, 584,
)


def _char_width(ch, bold):
    table = _HELV_B if bold else _HELV
    o = ord(ch)
    if 32 <= o <= 126:
        return table[o - 32]
    if ch == '\xa0':
        return table[0]
    return 611 if bold else 556


def _text_width(s, size, bold=False):
    return sum(_char_width(ch, bold) for ch in s) * size / 1000.0


def _esc(s):
    data = str(s).encode('cp1252', 'replace')
    out = bytearray()
    for b in data:
        if b in (0x28, 0x29, 0x5C):
            out.append(0x5C)
            out.append(b)
        elif b < 32 or b > 126:
            out.extend(('\\%03o' % b).encode('ascii'))
        else:
            out.append(b)
    return out.decode('ascii')


def _wrap(text, max_w, size, bold=False):
    text = '' if text is None else str(text)
    lines = []
    for para in text.split('\n'):
        words = para.split()
        if not words:
            lines.append('')
            continue
        cur = ''
        for word in words:
            cand = word if not cur else cur + ' ' + word
            if _text_width(cand, size, bold) <= max_w:
                cur = cand
                continue
            if cur:
                lines.append(cur)
                cur = ''
            if _text_width(word, size, bold) <= max_w:
                cur = word
            else:
                piece = ''
                for ch in word:
                    if _text_width(piece + ch, size, bold) <= max_w:
                        piece += ch
                    else:
                        if piece:
                            lines.append(piece)
                        piece = ch
                cur = piece
        if cur:
            lines.append(cur)
    return lines or ['']


def _text_op(x, y, s, size=9, bold=False, gray=0):
    font = '/F2' if bold else '/F1'
    return 'BT %s g %s %s Tf 1 0 0 1 %.2f %.2f Tm (%s) Tj ET' % (
        _num(gray), font, _num(size), x, y, _esc(s))


def _num(v):
    if isinstance(v, float):
        s = '%.2f' % v
        return s.rstrip('0').rstrip('.') if '.' in s else s
    return str(v)


def _rect_op(x, y, w, h, r, g, b):
    return 'q %s %s %s rg %s %s %s %s re f Q' % (
        _num(r), _num(g), _num(b), _num(x), _num(y), _num(w), _num(h))


def _line_op(x1, y1, x2, y2, gray=0.75, width=0.5):
    return 'q %s G %s w %s %s m %s %s l S Q' % (
        _num(gray), _num(width), _num(x1), _num(y1), _num(x2), _num(y2))


def _col_widths(columns, rows, avail):
    desired = []
    for i, col in enumerate(columns):
        w = _text_width(str(col), _HEADER_SIZE, True)
        for row in rows[:60]:
            w = max(w, min(_text_width(str(row[i]), _CELL_SIZE, False), 260))
        desired.append(max(w, 36))
    total = sum(desired) or 1
    factor = avail / total
    return [d * factor for d in desired]


def _pack_pairs(pairs, max_w, size):
    sep = '     '
    lines, cur = [], ''
    for label, value in pairs:
        item = '%s: %s' % (label, value)
        cand = item if not cur else cur + sep + item
        if _text_width(cand, size, False) <= max_w:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = item
    if cur:
        lines.append(cur)
    return lines or ['']


def build_report_pdf(title, subtitle, columns, rows, summary,
                     right_align=(), footer_left='', church_line=''):
    rows = [[('' if v is None else str(v)) for v in row] for row in rows]
    right_align = set(right_align)
    pages = [[]]
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    # ---------- first page header ----------
    ops = pages[0]
    y = PAGE_H - MARGIN_T
    ops.append(_text_op(MARGIN_L, y - 12, church_line or 'Grace Church Munyaka', 11.5, True))
    gen = 'Generated %s' % now
    ops.append(_text_op(PAGE_W - MARGIN_R - _text_width(gen, 8), y - 12, gen, 8, False, 0.4))
    y -= 34
    ops.append(_text_op(MARGIN_L, y, title, 17, True))
    y -= 15
    if subtitle:
        ops.append(_text_op(MARGIN_L, y, subtitle, 9, False, 0.35))
        y -= 14
    if summary:
        sum_lines = _pack_pairs(summary, CONTENT_W - 16, 9)
        box_h = len(sum_lines) * 12 + 8
        ops.append(_rect_op(MARGIN_L, y - box_h, CONTENT_W, box_h, 0.94, 0.93, 0.90))
        sy = y - box_h + 5
        for line in sum_lines:
            ops.append(_text_op(MARGIN_L + 8, sy, line, 9, False, 0.15))
            sy += 12
        y -= box_h + 8
    else:
        y -= 6

    # ---------- table ----------
    widths = _col_widths(columns, rows, CONTENT_W)
    xs = [MARGIN_L]
    for w in widths:
        xs.append(xs[-1] + w)

    def draw_header(top):
        bottom = top - _HEADER_H
        ops.append(_rect_op(MARGIN_L, bottom, CONTENT_W, _HEADER_H, 0.87, 0.87, 0.87))
        for i, col in enumerate(columns):
            tx = xs[i] + _PAD
            if i in right_align:
                tx = xs[i + 1] - _PAD - _text_width(str(col), _HEADER_SIZE, True)
            ops.append(_text_op(tx, bottom + 5.5, str(col), _HEADER_SIZE, True))
        return bottom

    def flush_grid(top, bottoms):
        if not bottoms:
            return
        span_bottom = bottoms[-1]
        hset = [top] + list(bottoms)
        for hy in hset:
            ops.append(_line_op(MARGIN_L, hy, PAGE_W - MARGIN_R, hy))
        for xv in xs:
            ops.append(_line_op(xv, top, xv, span_bottom))

    y = draw_header(y)
    seg_top = y + _HEADER_H
    seg_bottoms = [y]

    if not rows:
        ops.append(_text_op(MARGIN_L + 4, y - 14, 'No records found for the selected criteria.', 8.5, False, 0.45))

    for row in rows:
        cell_lines = [_wrap(row[i], widths[i] - 2 * _PAD, _CELL_SIZE) for i in range(len(columns))]
        n_lines = max(len(l) for l in cell_lines)
        rh = n_lines * _LEADING + 6
        if y - rh < BOTTOM:
            flush_grid(seg_top, seg_bottoms)
            pages.append([])
            ops = pages[-1]
            ops.append(_text_op(MARGIN_L, PAGE_H - MARGIN_T - 8, '%s (continued)' % title, 8.5, False, 0.45))
            y = PAGE_H - MARGIN_T - 22
            y = draw_header(y)
            seg_top = y + _HEADER_H
            seg_bottoms = [y]
        y -= rh
        for i, lines in enumerate(cell_lines):
            for k, line in enumerate(lines):
                if not line:
                    continue
                baseline = y + rh - 10 - _LEADING * k
                tx = xs[i] + _PAD
                if i in right_align:
                    tx = xs[i + 1] - _PAD - _text_width(line, _CELL_SIZE)
                ops.append(_text_op(tx, baseline, line, _CELL_SIZE))
        seg_bottoms.append(y)

    flush_grid(seg_top, seg_bottoms)

    # ---------- footers ----------
    total_pages = len(pages)
    for idx, p_ops in enumerate(pages):
        cy = 18
        p_ops.append(_line_op(MARGIN_L, cy + 14, PAGE_W - MARGIN_R, cy + 14, 0.85, 0.5))
        if footer_left:
            p_ops.append(_text_op(MARGIN_L, cy, footer_left, 7.5, False, 0.45))
        page_label = 'Page %d of %d' % (idx + 1, total_pages)
        p_ops.append(_text_op((PAGE_W - _text_width(page_label, 7.5)) / 2, cy, page_label, 7.5, False, 0.45))

    return _assemble(['\n'.join(p) for p in pages])


def _assemble(page_streams):
    objects = {}
    objects[1] = b'<< /Type /Catalog /Pages 2 0 R >>'
    objects[3] = (b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica '
                  b'/Encoding /WinAnsiEncoding >>')
    objects[4] = (b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold '
                  b'/Encoding /WinAnsiEncoding >>')

    kids = []
    num = 5
    for stream in page_streams:
        data = stream.encode('ascii')
        page_num, content_num = num, num + 1
        num += 2
        objects[page_num] = (
            '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] '
            '/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> '
            '/Contents %d 0 R >>' % (PAGE_W, PAGE_H, content_num)
        ).encode('ascii')
        objects[content_num] = b'<< /Length %d >>\nstream\n' % len(data) + data + b'\nendstream'
        kids.append('%d 0 R' % page_num)
    objects[2] = ('<< /Type /Pages /Kids [%s] /Count %d >>' % (
        ' '.join(kids), len(kids))).encode('ascii')

    out = bytearray(b'%PDF-1.4\n')
    offsets = {}
    for n in sorted(objects):
        offsets[n] = len(out)
        out += ('%d 0 obj\n' % n).encode('ascii')
        out += objects[n]
        out += b'\nendobj\n'
    xref_pos = len(out)
    max_n = max(objects)
    out += ('xref\n0 %d\n' % (max_n + 1)).encode('ascii')
    out += b'0000000000 65535 f \n'
    for n in range(1, max_n + 1):
        out += ('%010d 00000 n \n' % offsets[n]).encode('ascii')
    out += ('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n'
            % (max_n + 1, xref_pos)).encode('ascii')
    return bytes(out)