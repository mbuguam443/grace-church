import { Ionicons } from '@expo/vector-icons';
import { Stack, useFocusEffect, useLocalSearchParams } from 'expo-router';
import { useCallback, useState } from 'react';
import { Linking, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Btn, Card, Chip, ErrorBox, Field, Loading } from '../../components/ui';
import { useAuth } from '../../lib/auth';
import { api } from '../../lib/api';
import { Colors, formatDate, Radius, Spacing } from '../../lib/theme';
import { CourseComment, SundaySchoolCourse } from '../../lib/types';

export default function ClassScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { token } = useAuth();
  const [course, setCourse] = useState<SundaySchoolCourse | null>(null);
  const [comments, setComments] = useState<CourseComment[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [draft, setDraft] = useState('');

  const load = useCallback(async () => {
    if (!token || !id) return;
    try {
      const res = await api.sundaySchoolDetail(token, Number(id));
      setCourse(res.course);
      setComments(res.comments ?? []);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load this class.');
    }
  }, [token, id]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  async function join() {
    if (!token || !course) return;
    setBusy(true);
    setNotice(null);
    try {
      const res = await api.joinClass(token, course.id);
      setNotice(res.message);
      await load();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : 'Could not join this class.');
    } finally {
      setBusy(false);
    }
  }

  async function leave() {
    if (!token || !course) return;
    setBusy(true);
    setNotice(null);
    try {
      const res = await api.leaveClass(token, course.id);
      setNotice(res.message);
      await load();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : 'Could not leave this class.');
    } finally {
      setBusy(false);
    }
  }

  async function postComment() {
    if (!token || !course || !draft.trim()) return;
    setBusy(true);
    try {
      await api.addCourseComment(token, course.id, draft.trim());
      setDraft('');
      await load();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : 'Could not post your comment.');
    } finally {
      setBusy(false);
    }
  }

  async function removeComment(commentId: number) {
    if (!token || !course) return;
    try {
      await api.deleteCourseComment(token, course.id, commentId);
      await load();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : 'Could not delete that comment.');
    }
  }

  const mine = course?.my_enrollment ?? null;
  const iAmOnIt = mine && !mine.is_child;

  return (
    <View style={styles.safe}>
      <Stack.Screen options={{ title: 'Sunday School', headerShadowVisible: false }} />
      {error ? (
        <ErrorBox text={error} />
      ) : !course ? (
        <Loading />
      ) : (
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
          <View style={styles.hero}>
            <Text style={styles.heroKicker}>{course.age_group_label}</Text>
            <Text style={styles.heroTitle}>{course.title}</Text>
            {course.scripture ? <Text style={styles.heroByline}>{course.scripture}</Text> : null}
            <View style={styles.heroMeta}>
              {course.lesson_date ? <Chip label={formatDate(course.lesson_date)} bg="rgba(255,255,255,0.18)" color="#FFF" /> : null}
              <Chip label={`${course.enrolled_count} in class`} bg="rgba(255,255,255,0.18)" color="#FFF" />
              {course.spots_left !== null ? (
                <Chip label={`${course.spots_left} spots left`} bg="rgba(255,255,255,0.18)" color="#FFF" />
              ) : null}
            </View>
            <View style={styles.goldBar} />
          </View>

          <View style={styles.body}>
            {notice ? (
              <View style={styles.notice}>
                <Text style={styles.noticeText}>{notice}</Text>
              </View>
            ) : null}

            {mine ? (
              <Card style={styles.stateCard}>
                <Text style={styles.stateTitle}>
                  {mine.is_child ? `${mine.student_name} is in this class` : 'You are in this class'}
                </Text>
                <Text style={styles.stateSub}>
                  {mine.status === 'approved'
                    ? 'The lesson is unlocked below.'
                    : mine.status === 'pending'
                      ? 'Waiting for the teacher to approve.'
                      : 'Your request was not accepted.'}
                </Text>
                {iAmOnIt ? (
                  <Btn title="Leave this class" variant="outline" loading={busy} onPress={leave} />
                ) : null}
              </Card>
            ) : course.can_join ? (
              <Btn title={course.requires_approval ? 'Request to join' : 'Join this class'} loading={busy} onPress={join} />
            ) : course.is_full ? (
              <Card>
                <Text style={styles.stateSub}>This class is full. Please check back later.</Text>
              </Card>
            ) : !course.enable_registration ? (
              <Card>
                <Text style={styles.stateSub}>Registration is not open for this class.</Text>
              </Card>
            ) : null}

            {course.my_children_on_course && course.my_children_on_course.length ? (
              <View style={styles.chipWrap}>
                {course.my_children_on_course.map((name) => (
                  <Chip key={name} label={`${name} enrolled`} color={Colors.success} bg="#E4F5EA" />
                ))}
              </View>
            ) : null}

            {course.can_view_content ? (
              <>
                {course.memory_verse ? (
                  <View style={styles.verseBox}>
                    <Ionicons name="bookmark" size={16} color={Colors.gold} />
                    <View style={styles.verseTextWrap}>
                      <Text style={styles.verseLabel}>Memory verse</Text>
                      <Text style={styles.verseText}>{course.memory_verse}</Text>
                    </View>
                  </View>
                ) : null}
                {course.lesson ? <Section label="Lesson" icon="book" body={course.lesson} /> : null}
                {course.activities ? <Section label="Activities" icon="color-palette" body={course.activities} /> : null}
                {course.pdf_url || course.audio_url || course.video_file_url || course.video_url ? (
                  <View style={styles.actions}>
                    {course.video_url ? (
                      <Btn title="Watch the video" onPress={() => Linking.openURL(course.video_url!)} />
                    ) : null}
                    {course.video_file_url ? (
                      <Btn title="Play lesson video" variant="outline" onPress={() => Linking.openURL(course.video_file_url!)} />
                    ) : null}
                    {course.audio_url ? (
                      <Btn title="Listen to the audio" variant="outline" onPress={() => Linking.openURL(course.audio_url!)} />
                    ) : null}
                    {course.pdf_url ? (
                      <Btn title="Open the PDF" variant="outline" onPress={() => Linking.openURL(course.pdf_url!)} />
                    ) : null}
                  </View>
                ) : null}
              </>
            ) : (
              <Card style={styles.lockCard}>
                <Ionicons name="lock-closed-outline" size={26} color={Colors.muted} />
                <Text style={styles.stateTitle}>Lesson locked</Text>
                <Text style={styles.stateSub}>
                  Join this class (or have a child join) to read the lesson.
                </Text>
              </Card>
            )}

            <View style={styles.discussionHead}>
              <Text style={styles.sectionTitle}>Discussion</Text>
              <Chip label={`${comments.length}`} bg="#EEECE5" color={Colors.muted} />
            </View>

            <Field
              label="Add a comment or question"
              value={draft}
              onChangeText={setDraft}
              placeholder="Share with the class…"
              multiline
              style={styles.commentInput}
            />
            <Btn title="Post comment" loading={busy} disabled={!draft.trim()} onPress={postComment} />

            {comments.length === 0 ? (
              <Text style={styles.stateSub}>No comments yet. Be the first to say something.</Text>
            ) : (
              comments.map((c) => (
                <Card key={c.id} style={styles.commentCard}>
                  <View style={styles.commentTop}>
                    <Text style={styles.commentAuthor}>{c.author}</Text>
                    <Text style={styles.commentDate}>{formatDate(c.created_at)}</Text>
                  </View>
                  <Text style={styles.commentBody}>{c.body}</Text>
                  {c.can_delete ? (
                    <PressableText label="Delete" onPress={() => removeComment(c.id)} />
                  ) : null}
                </Card>
              ))
            )}
          </View>
        </ScrollView>
      )}
    </View>
  );
}

function PressableText({ label, onPress }: { label: string; onPress: () => void }) {
  return (
    <Text onPress={onPress} style={styles.deleteLink}>
      {label}
    </Text>
  );
}

function Section({ label, icon, body }: { label: string; icon: keyof typeof Ionicons.glyphMap; body: string }) {
  const blocks = body
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean);
  return (
    <View style={styles.section}>
      <View style={styles.sectionHead}>
        <Ionicons name={icon} size={14} color={Colors.navy} />
        <Text style={styles.sectionLabel}>{label}</Text>
      </View>
      {blocks.map((p, i) => (
        <Text key={i} style={styles.sectionBody}>
          {p}
        </Text>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  scroll: { paddingBottom: Spacing.xl },
  hero: { backgroundColor: Colors.navy, paddingHorizontal: Spacing.lg, paddingTop: Spacing.lg, paddingBottom: Spacing.xl },
  heroKicker: { fontSize: 12, fontWeight: '800', color: Colors.gold, textTransform: 'uppercase', letterSpacing: 0.8 },
  heroTitle: { fontSize: 26, fontWeight: '900', color: '#FFF', marginTop: Spacing.xs, lineHeight: 32 },
  heroByline: { fontSize: 14, color: 'rgba(255,255,255,0.85)', fontWeight: '600', marginTop: Spacing.sm },
  heroMeta: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm, marginTop: Spacing.md },
  goldBar: { marginTop: Spacing.lg, height: 3, width: 56, borderRadius: 999, backgroundColor: Colors.gold },
  body: { padding: Spacing.lg, gap: Spacing.md, marginTop: -Spacing.sm },
  notice: { backgroundColor: Colors.goldLight, borderRadius: Radius.md, padding: Spacing.md },
  noticeText: { fontSize: 13, color: Colors.text, fontWeight: '600' },
  stateCard: { gap: Spacing.sm },
  lockCard: { alignItems: 'center', gap: Spacing.sm, paddingVertical: Spacing.xl },
  stateTitle: { fontSize: 16, fontWeight: '800', color: Colors.text },
  stateSub: { fontSize: 13, color: Colors.muted, lineHeight: 19 },
  chipWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  verseBox: {
    backgroundColor: Colors.goldLight,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: Spacing.sm,
  },
  verseTextWrap: { flex: 1, gap: Spacing.xs },
  verseLabel: { fontSize: 11, fontWeight: '800', color: Colors.muted, textTransform: 'uppercase', letterSpacing: 0.5 },
  verseText: { fontSize: 16, lineHeight: 24, color: Colors.text, fontWeight: '700', fontStyle: 'italic' },
  section: {
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    gap: Spacing.md,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
    borderLeftWidth: 4,
    borderLeftColor: Colors.navy,
  },
  sectionHead: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  sectionLabel: { fontSize: 12, fontWeight: '800', color: Colors.navy, textTransform: 'uppercase', letterSpacing: 0.4 },
  sectionTitle: { fontSize: 16, fontWeight: '800', color: Colors.text },
  sectionBody: { fontSize: 16, lineHeight: 26, color: Colors.text },
  actions: { gap: Spacing.sm },
  discussionHead: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: Spacing.sm },
  commentInput: { minHeight: 88, textAlignVertical: 'top' },
  commentCard: { gap: Spacing.xs },
  commentTop: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  commentAuthor: { fontSize: 14, fontWeight: '800', color: Colors.text },
  commentDate: { fontSize: 12, color: Colors.muted },
  commentBody: { fontSize: 15, lineHeight: 22, color: Colors.text },
  deleteLink: { fontSize: 12, fontWeight: '700', color: Colors.danger, marginTop: Spacing.xs },
});
