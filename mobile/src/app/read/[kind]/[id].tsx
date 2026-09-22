import { Ionicons } from '@expo/vector-icons';
import { Stack, useFocusEffect, useLocalSearchParams } from 'expo-router';
import { useCallback, useState } from 'react';
import { Linking, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Btn, Chip, Loading } from '../../../components/ui';
import { useAuth } from '../../../lib/auth';
import { api } from '../../../lib/api';
import { moduleTitle } from '../../../lib/library';
import { Colors, formatDate, Radius, Spacing } from '../../../lib/theme';

const KIND_META: Record<string, { icon: keyof typeof Ionicons.glyphMap; label: string }> = {
  sermons: { icon: 'mic', label: 'Sermon' },
  'bible-study': { icon: 'book', label: 'Bible study' },
  devotions: { icon: 'sunny', label: 'Devotion' },
  songs: { icon: 'musical-notes', label: 'Song' },
};

export default function ReadScreen() {
  const { kind, id } = useLocalSearchParams<{ kind: string; id: string }>();
  const { token } = useAuth();
  const [item, setItem] = useState<Record<string, any> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const meta = KIND_META[kind] ?? { icon: 'document-text' as const, label: moduleTitle(kind) };

  const load = useCallback(async () => {
    if (!token || !id) return;
    try {
      const endpoint = kind === 'bible-study' ? `bible-study/${id}/` : kind === 'songs' ? `songs/${id}/` : `sermons/${id}/`;
      setItem(await api.detail<Record<string, any>>(token, endpoint));
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load the note.');
    }
  }, [token, kind, id]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  const title = item?.title ? String(item.title) : moduleTitle(kind);
  const verse = item?.bible_verse || item?.scripture;
  const byline = item?.speaker
    ? `By ${item.speaker}`
    : item?.teacher
      ? `Taught by ${item.teacher}`
      : item?.author
        ? String(item.author)
        : null;
  const date = item?.date || item?.study_date;

  return (
    <View style={styles.safe}>
      <Stack.Screen options={{ title: meta.label, headerShadowVisible: false }} />
      {error ? (
        <View style={styles.center}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      ) : !item ? (
        <Loading />
      ) : (
        <ScrollView contentContainerStyle={styles.scroll}>
          <View style={styles.hero}>
            <View style={styles.heroIcon}>
              <Ionicons name={meta.icon} size={22} color="#FFF" />
            </View>
            <Text style={styles.heroKicker}>{meta.label}</Text>
            <Text style={styles.heroTitle}>{title}</Text>
            {byline ? <Text style={styles.heroByline}>{byline}</Text> : null}
            <View style={styles.heroMeta}>
              {date ? <Chip label={formatDate(String(date))} bg="rgba(255,255,255,0.18)" color="#FFF" /> : null}
              {item.category_label ? <Chip label={String(item.category_label)} bg="rgba(255,255,255,0.18)" color="#FFF" /> : null}
              {item.category && kind !== 'songs' ? (
                <Chip label={String(item.category)} bg="rgba(255,255,255,0.18)" color="#FFF" />
              ) : null}
              {item.key ? <Chip label={`Key ${item.key}`} bg="rgba(255,255,255,0.18)" color="#FFF" /> : null}
              {item.tempo ? <Chip label={String(item.tempo)} bg="rgba(255,255,255,0.18)" color="#FFF" /> : null}
            </View>
            <View style={styles.goldBar} />
          </View>

          <View style={styles.body}>
            {verse ? (
              <View style={styles.verseBox}>
                <Ionicons name="bookmark" size={16} color={Colors.gold} />
                <Text style={styles.verseText}>{String(verse)}</Text>
              </View>
            ) : null}

            {kind === 'songs' ? (
              <View style={styles.lyricsBox}>
                {String(item.lyrics || 'Lyrics have not been added yet.')
                  .split('\n')
                  .map((line: string, i: number) => (
                    <Text key={i} style={[styles.lyricsLine, line.trim() === '' && styles.lyricsSpacer]}>
                      {line}
                    </Text>
                  ))}
              </View>
            ) : kind === 'bible-study' ? (
              <>
                {item.content ? <Article label="Study notes" icon="book" body={String(item.content)} /> : null}
                {item.key_points ? <Article label="Key points" icon="checkmark-circle" body={String(item.key_points)} /> : null}
                {item.prayer_points ? <Article label="Prayer points" icon="hand-left" body={String(item.prayer_points)} /> : null}
                {item.discussion_questions ? (
                  <Article label="Discussion questions" icon="chatbubbles" body={String(item.discussion_questions)} />
                ) : null}
              </>
            ) : (
              <>
                {item.description ? <Article label="About this message" icon="information-circle" body={String(item.description)} /> : null}
                {item.sermon_notes ? <Article label="Sermon notes" icon="document-text" body={String(item.sermon_notes)} /> : null}
                {!item.sermon_notes && !item.description ? (
                  <View style={styles.emptyBox}>
                    <Ionicons name="document-outline" size={28} color={Colors.muted} />
                    <Text style={styles.emptyText}>No notes published for this message yet.</Text>
                  </View>
                ) : null}
              </>
            )}

            {item.youtube_url || item.pdf_url ? (
              <View style={styles.actions}>
                {item.youtube_url ? (
                  <Btn title="Watch on YouTube" onPress={() => Linking.openURL(String(item.youtube_url))} />
                ) : null}
                {item.pdf_url ? (
                  <Btn title="Open study PDF" variant="outline" onPress={() => Linking.openURL(String(item.pdf_url))} />
                ) : null}
              </View>
            ) : null}
          </View>
        </ScrollView>
      )}
    </View>
  );
}

function Article({ label, icon, body }: { label: string; icon: keyof typeof Ionicons.glyphMap; body: string }) {
  const blocks = body
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean);
  return (
    <View style={styles.article}>
      <View style={styles.articleHead}>
        <View style={styles.articleIcon}>
          <Ionicons name={icon} size={14} color={Colors.navy} />
        </View>
        <Text style={styles.articleLabel}>{label}</Text>
      </View>
      {blocks.map((p, i) => (
        <Text key={i} style={styles.articleBody}>
          {p}
        </Text>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: Spacing.xl },
  errorText: { color: Colors.danger, fontSize: 14, textAlign: 'center' },
  scroll: { paddingBottom: Spacing.xl },
  hero: {
    backgroundColor: Colors.navy,
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.lg,
    paddingBottom: Spacing.xl,
  },
  heroIcon: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.16)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.md,
  },
  heroKicker: {
    fontSize: 12,
    fontWeight: '800',
    color: Colors.gold,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  heroTitle: { fontSize: 26, fontWeight: '900', color: '#FFF', marginTop: Spacing.xs, lineHeight: 32 },
  heroByline: { fontSize: 14, color: 'rgba(255,255,255,0.85)', fontWeight: '600', marginTop: Spacing.sm },
  heroMeta: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm, marginTop: Spacing.md },
  goldBar: { marginTop: Spacing.lg, height: 3, width: 56, borderRadius: 999, backgroundColor: Colors.gold },
  body: { padding: Spacing.lg, gap: Spacing.md, marginTop: -Spacing.sm },
  verseBox: {
    backgroundColor: Colors.goldLight,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: Spacing.sm,
  },
  verseText: { flex: 1, fontSize: 16, lineHeight: 24, color: Colors.text, fontWeight: '700', fontStyle: 'italic' },
  lyricsBox: {
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    paddingVertical: Spacing.xl,
    paddingHorizontal: Spacing.lg,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
  },
  lyricsLine: { fontSize: 16, lineHeight: 28, color: Colors.text, textAlign: 'center' },
  lyricsSpacer: { height: Spacing.md },
  article: {
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    gap: Spacing.md,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
    borderLeftWidth: 4,
    borderLeftColor: Colors.navy,
  },
  articleHead: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  articleIcon: {
    width: 28,
    height: 28,
    borderRadius: 8,
    backgroundColor: Colors.navySoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
  articleLabel: { fontSize: 12, fontWeight: '800', color: Colors.navy, textTransform: 'uppercase', letterSpacing: 0.4 },
  articleBody: { fontSize: 16, lineHeight: 26, color: Colors.text },
  emptyBox: {
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    padding: Spacing.xl,
    alignItems: 'center',
    gap: Spacing.sm,
  },
  emptyText: { color: Colors.muted, fontSize: 14, textAlign: 'center' },
  actions: { gap: Spacing.sm, marginTop: Spacing.xs },
});
