import { Ionicons } from '@expo/vector-icons';
import { Stack, useFocusEffect, useLocalSearchParams, useRouter } from 'expo-router';
import { useCallback, useState } from 'react';
import { FlatList, Pressable, RefreshControl, StyleSheet, Text, TextInput, View } from 'react-native';

import { Btn, Card, Chip, EmptyState, ErrorBox, Loading } from '../../components/ui';
import { useAuth } from '../../lib/auth';
import { api, ENDPOINTS } from '../../lib/api';
import { moduleTitle } from '../../lib/library';
import { Colors, formatDate, formatMoney, Radius, Shadow, Spacing } from '../../lib/theme';
import {
  Announcement,
  AttendanceRecord,
  BibleStudyNote,
  Child,
  ChurchEvent,
  ChurchService,
  DirectoryMember,
  Facility,
  FacilityBooking,
  GivingRecord,
  Group,
  Ministry,
  OnlineGiving,
  Prayer,
  Sermon,
  Song,
  SundaySchoolCourse,
} from '../../lib/types';

const READABLE_KINDS = ['sermons', 'bible-study', 'devotions', 'songs', 'sunday-school', 'groups-all', 'ministries', 'directory'];
const SEARCHABLE_KINDS = ['sermons', 'bible-study', 'devotions', 'songs', 'sunday-school', 'groups-all', 'ministries', 'directory', 'children'];
const KIND_ACCENT: Record<string, string> = {
  sermons: '#A8704A',
  'bible-study': '#6F42C1',
  devotions: '#D97706',
  songs: '#7E4F2D',
  'sunday-school': '#198754',
  children: '#198754',
  ministries: '#6F42C1',
  directory: '#8A7763',
};

export default function ListScreen() {
  const { kind } = useLocalSearchParams<{ kind: string }>();
  const { token } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<Record<string, unknown>[] | null>(null);
  const [count, setCount] = useState(0);
  const [total, setTotal] = useState<string | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [query, setQuery] = useState('');
  const [services, setServices] = useState<ChurchService[]>([]);

  const endpoint = ENDPOINTS[kind] ? ENDPOINTS[kind] : 'groups/';
  const readable = READABLE_KINDS.includes(kind);
  const searchable = SEARCHABLE_KINDS.includes(kind);

  const filtered = useCallback(() => {
    if (!data || !query.trim()) return data;
    const q = query.trim().toLowerCase();
    return data.filter((item) => Object.values(item).join(' ').toLowerCase().includes(q));
  }, [data, query]);

  const load = useCallback(async () => {
    if (!token) return;
    try {
      const res = await api.list<Record<string, unknown>>(token, endpoint);
      setData(res.results);
      setCount(res.count);
      setTotal(res.total);
      if (kind === 'attendance') {
        try {
          const sv = await api.list<ChurchService>(token, 'services/');
          setServices(sv.results);
        } catch {
          setServices([]);
        }
      }
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load records.');
    }
  }, [token, endpoint, kind]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  }, [load]);

  async function checkIn(serviceId: number) {
    if (!token) return;
    setBusyId(serviceId);
    try {
      await api.checkIn(token, serviceId);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not check in.');
    } finally {
      setBusyId(null);
    }
  }

  async function toggleRegister(eventId: number) {
    if (!token) return;
    setBusyId(eventId);
    try {
      await api.registerEvent(token, eventId);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Registration failed.');
    } finally {
      setBusyId(null);
    }
  }

  return (
    <View style={styles.safe}>
      <Stack.Screen
        options={{
          title: moduleTitle(kind),
          headerRight:
            kind === 'prayers' ? (
              () => (
                <Pressable onPress={() => router.push('/prayers/new')} hitSlop={10}>
                  <Ionicons name="add-circle" size={26} color={Colors.navy} />
                </Pressable>
              )
            ) : kind === 'facilities' ? (
              () => (
                <Pressable onPress={() => router.push('/bookings/new')} hitSlop={10}>
                  <Ionicons name="add-circle" size={26} color={Colors.navy} />
                </Pressable>
              )
            ) : kind === 'online-giving' ? (
              () => (
                <Pressable onPress={() => router.push('/give')} hitSlop={10}>
                  <Ionicons name="add-circle" size={26} color={Colors.navy} />
                </Pressable>
              )
            ) : undefined,
        }}
      />

      {error && !data ? (
        <ErrorBox text={error} />
      ) : !data ? (
        <Loading />
      ) : (
        <FlatList
          data={filtered() ?? data}
          keyExtractor={(item, i) => String((item as { id?: number }).id ?? i)}
          contentContainerStyle={styles.content}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.navy} />}
          ListHeaderComponent={
            <>
              {kind === 'attendance' ? (
                <View style={styles.checkBlock}>
                  <Text style={styles.checkHeading}>Today at church</Text>
                  {services.filter((s) => s.can_check_in || s.checked_in).length === 0 ? (
                    <Text style={styles.summaryText}>No service is open for check-in right now.</Text>
                  ) : (
                    services
                      .filter((s) => s.can_check_in || s.checked_in)
                      .map((s) => (
                        <Card key={s.id} style={styles.checkCard}>
                          <Text style={styles.title}>{s.name}</Text>
                          <Text style={styles.sub}>
                            {(s.start_time ? s.start_time.slice(0, 5) : 'Time TBA') +
                              (s.location ? ` · ${s.location}` : '')}
                          </Text>
                          {s.checked_in ? (
                            <Chip label="You're here" color={Colors.success} bg="#E4F5EA" />
                          ) : (
                            <Btn
                              title="I'm here — check in"
                              loading={busyId === s.id}
                              onPress={() => checkIn(s.id)}
                            />
                          )}
                        </Card>
                      ))
                  )}
                </View>
              ) : null}
              {searchable ? (
                <View style={styles.searchWrap}>
                  <Ionicons name="search" size={16} color={Colors.muted} />
                  <TextInput
                    value={query}
                    onChangeText={setQuery}
                    placeholder={`Search ${moduleTitle(kind).toLowerCase()}…`}
                    placeholderTextColor={Colors.muted}
                    style={styles.searchInput}
                    autoCapitalize="none"
                    autoCorrect={false}
                  />
                  {query ? (
                    <Pressable onPress={() => setQuery('')} hitSlop={8}>
                      <Ionicons name="close-circle" size={16} color={Colors.muted} />
                    </Pressable>
                  ) : null}
                </View>
              ) : null}
              {count === 0 ? null : (
                <View style={styles.summary}>
                  <Text style={styles.summaryText}>
                    {query.trim()
                      ? `${filtered()?.length ?? 0} of ${count} record${count === 1 ? '' : 's'}`
                      : `${count} record${count === 1 ? '' : 's'}`}
                  </Text>
                  {total !== undefined && <Text style={styles.summaryTotal}>{formatMoney(total)}</Text>}
                </View>
              )}
            </>
          }
          ListEmptyComponent={<EmptyState icon="folder-open-outline" text="No records yet." />}
          renderItem={({ item }) => {
            const id = String((item as { id: number }).id);
            return (
              <RowItem
                kind={kind}
                item={item as Record<string, any>}
                busy={busyId === (item as unknown as ChurchEvent).id}
                onRegister={() => toggleRegister((item as unknown as ChurchEvent).id)}
                onOpen={readable ? () => router.push(detailRoute(kind, id)) : undefined}
              />
            );
          }}
          ItemSeparatorComponent={() => <View style={styles.sep} />}
        />
      )}
    </View>
  );
}

function detailRoute(kind: string, id: string) {
  // Some modules need their own screen because they have actions (join, leave, check in).
  if (kind === 'sunday-school') return { pathname: '/sunday-school/[id]' as const, params: { id } };
  if (kind === 'ministries') return { pathname: '/ministries/[id]' as const, params: { id } };
  if (kind === 'directory') return { pathname: '/members/[id]' as const, params: { id } };
  if (kind === 'groups-all') return { pathname: '/groups/[id]' as const, params: { id } };
  return { pathname: '/read/[kind]/[id]' as const, params: { kind, id } };
}

function RowItem({
  kind,
  item,
  busy,
  onRegister,
  onOpen,
}: {
  kind: string;
  item: Record<string, any>;
  busy: boolean;
  onRegister: () => void;
  onOpen?: () => void;
}) {
  const accent = KIND_ACCENT[kind] || Colors.navy;
  const row = (
    <Card style={[styles.card, onOpen ? { borderLeftWidth: 4, borderLeftColor: accent } : null, Shadow]}>
      {renderBody(kind, item, busy, onRegister)}
    </Card>
  );
  if (!onOpen) return row;
  return (
    <Pressable onPress={onOpen} style={({ pressed }) => (pressed ? { opacity: 0.7 } : undefined)}>
      {row}
    </Pressable>
  );
}

function renderBody(kind: string, item: Record<string, any>, busy: boolean, onRegister: () => void) {
  switch (kind) {
    case 'groups': {
      const g = item as Group;
      return (
        <View style={styles.rowBody}>
          <RowLine icon="people-outline" title={g.name} />
          {g.leader ? <RowSub text={g.leader} /> : null}
          <RowSub text={`${g.meeting_day}${g.meeting_time ? ` · ${g.meeting_time}` : ''}${g.location ? ` · ${g.location}` : ''}`} />
          <Chip label={`${g.members_count} members`} />
        </View>
      );
    }
    case 'givings': {
      const it = item as GivingRecord;
      return (
        <View style={styles.rowBody}>
          <View style={styles.amountRow}>
            <Text style={styles.amount}>{formatMoney(it.amount)}</Text>
            <Chip label={it.category_label} />
          </View>
          <RowSub text={formatDate(it.date)} />
          <RowSub text={`via ${it.payment_method_label}${it.reference_number ? ` · ${it.reference_number}` : ''}`} />
        </View>
      );
    }
    case 'attendance': {
      const a = item as AttendanceRecord;
      return (
        <View style={styles.rowBody}>
          <RowLine icon="calendar-outline" title={a.service} />
          <RowSub text={formatDate(a.date)} />
          {a.location ? <RowSub text={a.location} /> : null}
        </View>
      );
    }
    case 'events': {
      const e = item as ChurchEvent;
      return (
        <View style={styles.rowBody}>
          <RowLine icon="megaphone-outline" title={e.name} />
          <RowSub text={formatDate(e.date)} />
          <RowSub text={e.location || 'GC'} />
          <View style={styles.eventFooter}>
            <Chip
              label={e.registration_required ? (e.registered ? 'Registered' : 'Registration open') : 'No signup needed'}
              color={e.registered ? Colors.success : e.registration_required ? Colors.navy : Colors.muted}
              bg={e.registered ? '#E5F2E6' : Colors.goldLight}
            />
            {e.registration_required && e.registered ? (
              <Btn title="Cancel" variant="outline" style={styles.smallBtn} loading={busy} onPress={onRegister} />
            ) : null}
            {e.registration_required && !e.registered ? (
              <Btn title="Register" style={styles.smallBtn} loading={busy} onPress={onRegister} />
            ) : null}
          </View>
        </View>
      );
    }
    case 'announcements': {
      const a = item as Announcement;
      return (
        <View style={styles.rowBody}>
          <RowLine icon="checkbox" title={a.title} />
          <RowSub text={a.message} />
          <RowSub text={`Published ${formatDate(a.publish_date)}${a.target_audience ? ` · ${a.target_audience}` : ''}`} />
        </View>
      );
    }
    case 'sermons': {
      const s = item as Sermon;
      return (
        <StudyCard
          kicker={s.series || s.category || 'Sermon'}
          title={s.title}
          verse={s.bible_verse}
          meta={[s.speaker, formatDate(s.date)].filter(Boolean).join(' · ')}
          action="Open notes"
          accent={KIND_ACCENT.sermons}
        />
      );
    }
    case 'bible-study': {
      const n = item as BibleStudyNote;
      return (
        <StudyCard
          kicker={n.series || 'Bible study'}
          title={n.title}
          verse={n.bible_verse}
          meta={[n.teacher ? `Taught by ${n.teacher}` : '', formatDate(n.study_date)].filter(Boolean).join(' · ')}
          action="Open study"
          accent={KIND_ACCENT['bible-study']}
        />
      );
    }
    case 'devotions': {
      const s = item as Sermon;
      return (
        <StudyCard
          kicker="Devotion"
          title={s.title}
          verse={s.bible_verse}
          meta={[s.speaker, formatDate(s.date)].filter(Boolean).join(' · ')}
          action="Open devotion"
          accent={KIND_ACCENT.devotions}
        />
      );
    }
    case 'songs': {
      const song = item as Song;
      return (
        <StudyCard
          kicker={song.category_label || 'Song'}
          title={song.title}
          verse={song.scripture}
          meta={[song.author, song.key ? `Key ${song.key}` : ''].filter(Boolean).join(' · ')}
          action="Open lyrics"
          accent={KIND_ACCENT.songs}
        />
      );
    }
    case 'prayers': {
      const p = item as Prayer;
      return (
        <View style={styles.rowBody}>
          <RowLine icon="chatbubbles-outline" title={p.title} />
          <RowSub text={p.request} />
          <View style={styles.eventFooter}>
            <Chip label={p.category_label} />
            <Chip label={p.status_label} color={p.status === 'answered' ? Colors.success : Colors.info} bg="#E7EDF7" />
            <Chip label={formatDate(p.date)} bg="#EEECE5" color={Colors.muted} />
          </View>
        </View>
      );
    }
    case 'sunday-school': {
      const c = item as SundaySchoolCourse;
      const mine = c.my_enrollment;
      return (
        <View style={styles.rowBody}>
          <Text style={[styles.kicker, { color: KIND_ACCENT['sunday-school'] }]}>
            {c.age_group_label}
          </Text>
          <RowLine icon="school-outline" title={c.title} />
          {c.scripture ? <RowSub text={c.scripture} /> : null}
          <View style={styles.eventFooter}>
            {c.lesson_date ? <Chip label={formatDate(c.lesson_date)} bg="#EEECE5" color={Colors.muted} /> : null}
            <Chip label={`${c.enrolled_count} in class`} />
            {c.spots_left !== null ? <Chip label={`${c.spots_left} spots left`} color={Colors.success} bg="#E4F5EA" /> : null}
            {mine ? (
              <Chip
                label={`${mine.student_name} · ${mine.status_label}`}
                color={mine.status === 'approved' ? Colors.success : '#B5651D'}
                bg={mine.status === 'approved' ? '#E4F5EA' : '#F7E6DC'}
              />
            ) : c.can_join ? (
              <Chip label="Open to join" color={Colors.navy} bg={Colors.goldLight} />
            ) : c.is_full ? (
              <Chip label="Class full" color={Colors.danger} bg="#F7E6DC" />
            ) : null}
          </View>
        </View>
      );
    }
    case 'children': {
      const ch = item as Child;
      return (
        <View style={styles.rowBody}>
          <RowLine icon="happy-outline" title={ch.full_name} />
          <RowSub text={`${ch.age} yrs · ${ch.age_group_label}${ch.school_class ? ` · ${ch.school_class}` : ''}`} />
          {ch.classes.length ? (
            <View style={styles.eventFooter}>
              {ch.classes.map((c) => (
                <Chip key={c.id} label={c.title} color={c.status === 'approved' ? Colors.success : '#B5651D'} bg="#E4F5EA" />
              ))}
            </View>
          ) : null}
          <View style={styles.eventFooter}>
            {ch.checked_in_today ? (
              <Chip label={ch.checked_out_today ? 'Checked out' : `Checked in ${ch.checkin_time ?? ''}`} color={Colors.success} bg="#E4F5EA" />
            ) : (
              <Chip label="Not checked in" color={Colors.muted} bg="#EEECE5" />
            )}
          </View>
        </View>
      );
    }
    case 'ministries': {
      const m = item as Ministry;
      return (
        <View style={styles.rowBody}>
          <RowLine icon="hand-left-outline" title={m.name} />
          {m.leader ? <RowSub text={`Led by ${m.leader}`} /> : null}
          {m.description ? <RowSub text={m.description} /> : null}
        </View>
      );
    }
    case 'facilities': {
      const f = item as Facility;
      return (
        <View style={styles.rowBody}>
          <RowLine icon="business-outline" title={f.name} />
          <RowSub text={[f.location, f.capacity ? `Seats ${f.capacity}` : null].filter(Boolean).join(' · ')} />
          {f.description ? <RowSub text={f.description} /> : null}
        </View>
      );
    }
    case 'my-bookings': {
      const b = item as FacilityBooking;
      return (
        <View style={styles.rowBody}>
          <RowLine icon="calendar-number-outline" title={b.event_name} />
          <RowSub text={`${formatDate(b.date)} · ${b.start_time} - ${b.end_time}`} />
          <RowSub text={b.facility} />
          <Chip label={b.status_label} color={b.status === 'approved' ? Colors.success : Colors.muted} bg="#EEECE5" />
        </View>
      );
    }
    case 'online-giving': {
      const g = item as OnlineGiving;
      return (
        <View style={styles.rowBody}>
          <View style={styles.amountRow}>
            <Text style={styles.amount}>{formatMoney(g.amount)}</Text>
            <Chip label={g.giving_category_label} />
          </View>
          <RowSub text={`${formatDate(g.created_at)} · ${g.frequency_label}`} />
          <RowSub text={g.reference_number} />
        </View>
      );
    }
    case 'directory': {
      const m = item as DirectoryMember;
      return (
        <View style={styles.rowBody}>
          <RowLine icon="person-outline" title={m.full_name} />
          <RowSub text={[m.phone, m.email].filter(Boolean).join(' · ')} />
          {m.member_number ? <RowSub text={`No. ${m.member_number}`} /> : null}
        </View>
      );
    }
    default:
      return <RowLine icon="albums-outline" title={String(item.title ?? 'Record')} />;
  }
}

function StudyCard({
  kicker,
  title,
  verse,
  meta,
  action,
  accent,
}: {
  kicker: string;
  title: string;
  verse?: string | null;
  meta?: string;
  action: string;
  accent: string;
}) {
  return (
    <View style={styles.studyBody}>
      <Text style={[styles.kicker, { color: accent }]}>{kicker}</Text>
      <Text style={styles.studyTitle}>{title}</Text>
      {verse ? (
        <View style={styles.verseStrip}>
          <Ionicons name="bookmark" size={14} color={Colors.gold} />
          <Text style={styles.verseStripText}>{verse}</Text>
        </View>
      ) : null}
      {meta ? <Text style={styles.studyMeta}>{meta}</Text> : null}
      <View style={styles.readHint}>
        <Text style={[styles.readHintText, { color: accent }]}>{action}</Text>
        <Ionicons name="arrow-forward" size={14} color={accent} />
      </View>
    </View>
  );
}

function RowLine({ icon, title }: { icon: string; title: string }) {
  return (
    <View style={styles.titleRow}>
      <Ionicons name={icon as keyof typeof Ionicons.glyphMap} size={16} color={Colors.navy} />
      <Text style={styles.title}>{title}</Text>
    </View>
  );
}

function RowSub({ text }: { text: string }) {
  return <Text style={styles.sub}>{text}</Text>;
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  content: { padding: Spacing.lg, paddingBottom: Spacing.xl },
  searchWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: Colors.card,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: Radius.md,
    paddingHorizontal: Spacing.md,
    marginBottom: Spacing.md,
  },
  searchInput: { flex: 1, paddingVertical: Spacing.sm + 2, fontSize: 14, color: Colors.text },
  summary: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    marginBottom: Spacing.sm,
    paddingHorizontal: Spacing.xs,
  },
  summaryText: { fontSize: 13, color: Colors.muted, fontWeight: '600' },
  summaryTotal: { fontSize: 15, fontWeight: '800', color: Colors.navy },
  sep: { height: Spacing.sm },
  checkBlock: { gap: Spacing.sm, marginBottom: Spacing.md },
  checkHeading: { fontSize: 13, fontWeight: '800', color: Colors.text, textTransform: 'uppercase', letterSpacing: 0.4 },
  checkCard: { gap: Spacing.sm, marginBottom: Spacing.xs },
  card: { gap: Spacing.sm + 2 },
  studyBody: { gap: Spacing.sm },
  kicker: { fontSize: 11, fontWeight: '800', textTransform: 'uppercase', letterSpacing: 0.7 },
  studyTitle: { fontSize: 18, fontWeight: '800', color: Colors.text, lineHeight: 24 },
  verseStrip: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: Spacing.sm,
    backgroundColor: Colors.goldLight,
    borderRadius: Radius.sm,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
  },
  verseStripText: { flex: 1, fontSize: 13, fontWeight: '700', fontStyle: 'italic', color: Colors.text, lineHeight: 18 },
  studyMeta: { fontSize: 13, color: Colors.muted, fontWeight: '600' },
  readHint: { flexDirection: 'row', alignItems: 'center', gap: Spacing.xs, marginTop: Spacing.xs },
  readHintText: { fontSize: 13, fontWeight: '800' },
  rowBody: { gap: Spacing.xs },
  titleRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  title: { flex: 1, fontSize: 15, fontWeight: '800', color: Colors.text },
  sub: { fontSize: 13, color: Colors.muted, lineHeight: 18 },
  amountRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: Spacing.sm },
  amount: { fontSize: 20, fontWeight: '900', color: Colors.navy },
  eventFooter: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', gap: Spacing.sm, marginTop: Spacing.xs },
  smallBtn: { height: 34, paddingHorizontal: Spacing.md },
});