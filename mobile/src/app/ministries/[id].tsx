import { Ionicons } from '@expo/vector-icons';
import { Stack, useLocalSearchParams, router } from 'expo-router';
import { useEffect, useState } from 'react';
import { Image } from 'expo-image';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Btn, Card, EmptyState, ErrorBox, Loading } from '../../components/ui';
import { useAuth } from '../../lib/auth';
import { api } from '../../lib/api';
import { Colors, Spacing } from '../../lib/theme';
import { DirectoryMember, Ministry } from '../../lib/types';

export default function MinistryScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { token } = useAuth();
  const [ministry, setMinistry] = useState<Ministry | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !id) return;
    (async () => {
      try {
        const res = await api.ministry(token, Number(id));
        setMinistry(res.ministry);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Could not load this ministry.');
      }
    })();
  }, [token, id]);

  return (
    <View style={styles.safe}>
      <Stack.Screen options={{ title: ministry?.name ?? 'Ministry', headerShadowVisible: false }} />
      {error ? (
        <ErrorBox text={error} />
      ) : !ministry ? (
        <Loading />
      ) : (
        <ScrollView contentContainerStyle={styles.scroll}>
          {ministry.image_url ? (
            <Image source={{ uri: ministry.image_url }} style={styles.cover} contentFit="cover" />
          ) : null}
          <View style={[styles.hero, !ministry.image_url && styles.heroNoImage]}>
            <Text style={styles.heroKicker}>Ministry</Text>
            <Text style={styles.heroTitle}>{ministry.name}</Text>
            {ministry.leader ? <Text style={styles.heroByline}>Led by {ministry.leader}</Text> : null}
            <View style={styles.goldBar} />
          </View>

          <View style={styles.body}>
            {ministry.description ? <Text style={styles.description}>{ministry.description}</Text> : null}

            <Text style={styles.sectionTitle}>Serve with us</Text>
            <Text style={styles.sub}>
              Talk to the ministry leader or the church office if you would like to join this team.
            </Text>
            {ministry.leader ? (
              <Btn title="See the leader in the directory" onPress={() => router.push('/list/directory')} />
            ) : null}

            <Text style={styles.sectionTitle}>Team members</Text>
            {(ministry.members ?? []).length === 0 ? (
              <EmptyState icon="hand-left-outline" text="No members listed yet." />
            ) : (
              (ministry.members ?? []).map((m: DirectoryMember) => (
                <Pressable key={m.id} onPress={() => router.push({ pathname: '/members/[id]', params: { id: String(m.id) } })}>
                  <Card style={styles.memberCard}>
                    <View style={styles.memberRow}>
                      <Ionicons name="person-circle-outline" size={24} color={Colors.navy} />
                      <View style={styles.memberText}>
                        <Text style={styles.memberName}>{m.full_name}</Text>
                        <Text style={styles.sub}>{[m.phone, m.email].filter(Boolean).join(' · ') || 'No contact on file'}</Text>
                      </View>
                      <Ionicons name="chevron-forward" size={18} color={Colors.muted} />
                    </View>
                  </Card>
                </Pressable>
              ))
            )}
            <Text style={styles.privacy}>
              <Ionicons name="information-circle-outline" size={13} color={Colors.muted} /> Call or email a team member to
              get involved.
            </Text>
          </View>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  scroll: { paddingBottom: Spacing.xl },
  cover: { width: '100%', height: 180 },
  hero: { backgroundColor: Colors.navy, paddingHorizontal: Spacing.lg, paddingVertical: Spacing.xl, gap: Spacing.xs },
  heroNoImage: { marginTop: 0 },
  heroKicker: { fontSize: 12, fontWeight: '800', color: Colors.gold, textTransform: 'uppercase', letterSpacing: 0.8 },
  heroTitle: { fontSize: 26, fontWeight: '900', color: '#FFF', lineHeight: 32 },
  heroByline: { fontSize: 14, color: 'rgba(255,255,255,0.85)', fontWeight: '600', marginTop: Spacing.xs },
  goldBar: { marginTop: Spacing.lg, height: 3, width: 56, borderRadius: 999, backgroundColor: Colors.gold },
  body: { padding: Spacing.lg, gap: Spacing.md, marginTop: -Spacing.sm },
  description: { fontSize: 15, lineHeight: 24, color: Colors.text },
  sectionTitle: { fontSize: 15, fontWeight: '800', color: Colors.text, marginTop: Spacing.sm },
  sub: { fontSize: 13, color: Colors.muted, lineHeight: 19 },
  memberCard: { marginBottom: Spacing.sm },
  memberRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  memberText: { flex: 1, gap: 2 },
  memberName: { fontSize: 15, fontWeight: '800', color: Colors.text },
  privacy: { fontSize: 12, color: Colors.muted, lineHeight: 18 },
});
