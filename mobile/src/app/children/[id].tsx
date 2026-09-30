import { Ionicons } from '@expo/vector-icons';
import { Stack, useFocusEffect, useLocalSearchParams } from 'expo-router';
import { useCallback, useState } from 'react';
import { Image } from 'expo-image';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { Btn, Card, Chip, ErrorBox, Loading } from '../../components/ui';
import { useAuth } from '../../lib/auth';
import { api } from '../../lib/api';
import { Colors, formatDate, initials, Radius, Spacing } from '../../lib/theme';
import { Child } from '../../lib/types';

export default function ChildScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { token } = useAuth();
  const [child, setChild] = useState<Child | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    if (!token || !id) return;
    try {
      const res = await api.detail<{ child: Child }>(token, `children/${id}/`);
      setChild(res.child);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load this child.');
    }
  }, [token, id]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  async function checkIn() {
    if (!token || !child) return;
    setBusy(true);
    setNotice(null);
    try {
      await api.checkInChild(token, child.id);
      await load();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : 'Could not check in.');
    } finally {
      setBusy(false);
    }
  }

  async function checkOut() {
    if (!token || !child) return;
    setBusy(true);
    setNotice(null);
    try {
      await api.checkOutChild(token, child.id);
      await load();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : 'Could not check out.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={styles.safe}>
      <Stack.Screen options={{ title: child?.first_name ?? 'Child', headerShadowVisible: false }} />
      {error ? (
        <ErrorBox text={error} />
      ) : !child ? (
        <Loading />
      ) : (
        <ScrollView contentContainerStyle={styles.scroll}>
          <View style={styles.hero}>
            {child.photo_url ? (
              <Image source={{ uri: child.photo_url }} style={styles.photo} contentFit="cover" />
            ) : (
              <View style={styles.photoFallback}>
                <Text style={styles.photoText}>{initials(child.full_name)}</Text>
              </View>
            )}
            <Text style={styles.heroTitle}>{child.full_name}</Text>
            <View style={styles.heroMeta}>
              <Chip label={`${child.age} years`} bg="rgba(255,255,255,0.18)" color="#FFF" />
              <Chip label={child.age_group_label} bg="rgba(255,255,255,0.18)" color="#FFF" />
              {child.school_class ? <Chip label={child.school_class} bg="rgba(255,255,255,0.18)" color="#FFF" /> : null}
            </View>
            <View style={styles.goldBar} />
          </View>

          <View style={styles.body}>
            {notice ? (
              <View style={styles.notice}>
                <Text style={styles.noticeText}>{notice}</Text>
              </View>
            ) : null}

            <Card style={styles.statusCard}>
              <View style={styles.statusRow}>
                <Ionicons
                  name={child.checked_in_today ? (child.checked_out_today ? 'checkmark-done-circle' : 'checkmark-circle') : 'time-outline'}
                  size={22}
                  color={child.checked_in_today ? Colors.success : Colors.muted}
                />
                <View style={styles.statusText}>
                  <Text style={styles.statusTitle}>
                    {child.checked_out_today ? 'Checked out' : child.checked_in_today ? 'Checked in' : 'Not checked in'}
                  </Text>
                  <Text style={styles.statusSub}>
                    {child.checkin_time ? `Checked in at ${child.checkin_time} today` : 'Check in when you drop them off'}
                  </Text>
                </View>
              </View>
              {child.checked_in_today && !child.checked_out_today ? (
                <Btn title="Check out" variant="outline" loading={busy} onPress={checkOut} />
              ) : (
                <Btn title="Check in" loading={busy} onPress={checkIn} />
              )}
            </Card>

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Sunday School</Text>
              {child.classes.length === 0 ? (
                <Text style={styles.sub}>Not on a class yet. A teacher can add them from the Sunday School page.</Text>
              ) : (
                child.classes.map((c) => (
                  <View key={c.id} style={styles.classRow}>
                    <Ionicons name="school-outline" size={18} color={Colors.navy} />
                    <View style={styles.classText}>
                      <Text style={styles.className}>{c.title}</Text>
                      <Text style={styles.sub}>{c.age_group_label}</Text>
                    </View>
                    <Chip
                      label={c.status_label}
                      color={c.status === 'approved' ? Colors.success : Colors.muted}
                      bg={c.status === 'approved' ? '#E4F5EA' : '#EEECE5'}
                    />
                  </View>
                ))
              )}
            </View>

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Details</Text>
              <DetailRow label="Date of birth" value={formatDate(child.date_of_birth)} />
              <DetailRow label="Gender" value={child.gender} />
              <DetailRow label="Teacher" value={child.teacher} />
              <DetailRow label="Allergies" value={child.allergies} />
              <DetailRow label="Emergency contact" value={child.emergency_contact} />
            </View>
          </View>
        </ScrollView>
      )}
    </View>
  );
}

function DetailRow({ label, value }: { label: string; value?: string | null }) {
  if (!value) return null;
  return (
    <View style={styles.detailRow}>
      <Text style={styles.detailLabel}>{label}</Text>
      <Text style={styles.detailValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  scroll: { paddingBottom: Spacing.xl },
  hero: {
    backgroundColor: Colors.navy,
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.lg,
    paddingBottom: Spacing.xl,
    alignItems: 'center',
  },
  photo: { width: 96, height: 96, borderRadius: 48, marginBottom: Spacing.md },
  photoFallback: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: 'rgba(255,255,255,0.18)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.md,
  },
  photoText: { fontSize: 30, fontWeight: '900', color: '#FFF' },
  heroTitle: { fontSize: 24, fontWeight: '900', color: '#FFF', textAlign: 'center' },
  heroMeta: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm, marginTop: Spacing.md, justifyContent: 'center' },
  goldBar: { marginTop: Spacing.lg, height: 3, width: 56, borderRadius: 999, backgroundColor: Colors.gold },
  body: { padding: Spacing.lg, gap: Spacing.md, marginTop: -Spacing.sm },
  notice: { backgroundColor: Colors.goldLight, borderRadius: Radius.md, padding: Spacing.md },
  noticeText: { fontSize: 13, color: Colors.text, fontWeight: '600' },
  statusCard: { gap: Spacing.md },
  statusRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  statusText: { flex: 1, gap: 2 },
  statusTitle: { fontSize: 16, fontWeight: '800', color: Colors.text },
  statusSub: { fontSize: 13, color: Colors.muted },
  section: {
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    gap: Spacing.sm,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
  },
  sectionTitle: { fontSize: 15, fontWeight: '800', color: Colors.text, marginBottom: Spacing.xs },
  classRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, paddingVertical: Spacing.xs },
  classText: { flex: 1, gap: 2 },
  className: { fontSize: 14, fontWeight: '700', color: Colors.text },
  sub: { fontSize: 13, color: Colors.muted, lineHeight: 19 },
  detailRow: { flexDirection: 'row', justifyContent: 'space-between', gap: Spacing.md, paddingVertical: Spacing.xs },
  detailLabel: { fontSize: 13, color: Colors.muted, fontWeight: '600' },
  detailValue: { flex: 1, fontSize: 13, color: Colors.text, fontWeight: '700', textAlign: 'right' },
});
