import { Ionicons } from '@expo/vector-icons';
import { Stack, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { Linking, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Btn, Card, Chip, EmptyState, ErrorBox, Loading } from '../../components/ui';
import { useAuth } from '../../lib/auth';
import { api } from '../../lib/api';
import { Colors, Spacing } from '../../lib/theme';
import { GroupDetail } from '../../lib/types';

export default function GroupScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { token } = useAuth();
  const [group, setGroup] = useState<GroupDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !id) return;
    (async () => {
      try {
        const res = await api.groupDetail(token, Number(id));
        setGroup(res.group);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Could not load this group.');
      }
    })();
  }, [token, id]);

  return (
    <View style={styles.safe}>
      <Stack.Screen options={{ title: group?.name ?? 'Group', headerShadowVisible: false }} />
      {error ? (
        <ErrorBox text={error} />
      ) : !group ? (
        <Loading />
      ) : (
        <ScrollView contentContainerStyle={styles.scroll}>
          <View style={styles.hero}>
            <Text style={styles.heroKicker}>Fellowship</Text>
            <Text style={styles.heroTitle}>{group.name}</Text>
            <View style={styles.heroMeta}>
              <Chip label={`${group.members_count} members`} bg="rgba(255,255,255,0.18)" color="#FFF" />
              {group.leader ? <Chip label={`Led by ${group.leader}`} bg="rgba(255,255,255,0.18)" color="#FFF" /> : null}
            </View>
            <View style={styles.goldBar} />
          </View>

          <View style={styles.body}>
            {group.description ? <Text style={styles.description}>{group.description}</Text> : null}

            <Card style={styles.meetCard}>
              <View style={styles.meetRow}>
                <Ionicons name="repeat-outline" size={18} color={Colors.navy} />
                <View style={styles.meetText}>
                  <Text style={styles.meetLabel}>Meets</Text>
                  <Text style={styles.meetValue}>
                    {[group.meeting_day, group.meeting_time, group.location].filter(Boolean).join(' · ') || 'Contact the leader for details'}
                  </Text>
                </View>
              </View>
            </Card>

            <Text style={styles.sectionTitle}>Members</Text>
            {group.members.length === 0 ? (
              <EmptyState icon="people-outline" text="No members listed yet." />
            ) : (
              group.members.map((m) => (
                <Card key={m.id} style={styles.memberCard}>
                  <Text style={styles.memberName}>{m.full_name}</Text>
                  {m.phone ? <Btn title={`Call ${m.phone}`} variant="outline" onPress={() => Linking.openURL(`tel:${m.phone}`)} /> : null}
                  {m.email ? <Btn title={`Email ${m.email}`} variant="outline" onPress={() => Linking.openURL(`mailto:${m.email}`)} /> : null}
                </Card>
              ))
            )}
          </View>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  scroll: { paddingBottom: Spacing.xl },
  hero: { backgroundColor: Colors.navy, paddingHorizontal: Spacing.lg, paddingVertical: Spacing.xl, gap: Spacing.xs },
  heroKicker: { fontSize: 12, fontWeight: '800', color: Colors.gold, textTransform: 'uppercase', letterSpacing: 0.8 },
  heroTitle: { fontSize: 26, fontWeight: '900', color: '#FFF', lineHeight: 32 },
  heroMeta: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm, marginTop: Spacing.md },
  goldBar: { marginTop: Spacing.lg, height: 3, width: 56, borderRadius: 999, backgroundColor: Colors.gold },
  body: { padding: Spacing.lg, gap: Spacing.md, marginTop: -Spacing.sm },
  description: { fontSize: 15, lineHeight: 24, color: Colors.text },
  meetCard: { backgroundColor: Colors.goldLight, borderWidth: 0 },
  meetRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  meetText: { flex: 1, gap: 2 },
  meetLabel: { fontSize: 11, fontWeight: '800', color: Colors.muted, textTransform: 'uppercase', letterSpacing: 0.5 },
  meetValue: { fontSize: 14, fontWeight: '700', color: Colors.text, lineHeight: 20 },
  sectionTitle: { fontSize: 15, fontWeight: '800', color: Colors.text, marginTop: Spacing.sm },
  memberCard: { gap: Spacing.sm },
  memberName: { fontSize: 15, fontWeight: '800', color: Colors.text },
});
