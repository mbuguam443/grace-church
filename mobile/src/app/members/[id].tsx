import { Ionicons } from '@expo/vector-icons';
import { Stack, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { Image } from 'expo-image';
import { Linking, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Btn, Card, Chip, ErrorBox, Loading } from '../../components/ui';
import { useAuth } from '../../lib/auth';
import { api } from '../../lib/api';
import { Colors, initials, Spacing } from '../../lib/theme';
import { DirectoryMember } from '../../lib/types';

export default function MemberScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { token, user } = useAuth();
  const [member, setMember] = useState<DirectoryMember | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !id) return;
    (async () => {
      try {
        const res = await api.memberDetail(token, Number(id));
        setMember(res.member);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Could not load this member.');
      }
    })();
  }, [token, id]);

  const isMe = user?.id === Number(id);

  return (
    <View style={styles.safe}>
      <Stack.Screen options={{ title: member?.first_name ?? 'Member', headerShadowVisible: false }} />
      {error ? (
        <ErrorBox text={error} />
      ) : !member ? (
        <Loading />
      ) : (
        <ScrollView contentContainerStyle={styles.scroll}>
          <View style={styles.hero}>
            {member.photo_url ? (
              <Image source={{ uri: member.photo_url }} style={styles.photo} contentFit="cover" />
            ) : (
              <View style={styles.photoFallback}>
                <Text style={styles.photoText}>{initials(member.full_name)}</Text>
              </View>
            )}
            <Text style={styles.heroTitle}>{member.full_name}</Text>
            <View style={styles.heroMeta}>
              {member.member_number ? <Chip label={`No. ${member.member_number}`} bg="rgba(255,255,255,0.18)" color="#FFF" /> : null}
              <Chip label={member.membership_status_label} bg="rgba(255,255,255,0.18)" color="#FFF" />
              {member.gender ? <Chip label={member.gender} bg="rgba(255,255,255,0.18)" color="#FFF" /> : null}
            </View>
            <View style={styles.goldBar} />
          </View>

          <View style={styles.body}>
            <Card style={styles.card}>
              <Text style={styles.cardTitle}>Contact</Text>
              {member.phone ? (
                <Btn title={`Call ${member.phone}`} onPress={() => Linking.openURL(`tel:${member.phone}`)} />
              ) : null}
              {member.email ? (
                <Btn title={`Email ${member.email}`} variant="outline" onPress={() => Linking.openURL(`mailto:${member.email}`)} />
              ) : null}
              {!member.phone && !member.email ? <Text style={styles.sub}>No contact details on file.</Text> : null}
            </Card>
            {isMe ? (
              <Text style={styles.sub}>This is your own profile. You can update your details from the Profile tab.</Text>
            ) : null}
            <Text style={styles.privacy}>
              <Ionicons name="shield-checkmark-outline" size={13} color={Colors.muted} /> Home addresses and emergency
              contacts are never shown here.
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
  card: { gap: Spacing.sm },
  cardTitle: { fontSize: 15, fontWeight: '800', color: Colors.text },
  sub: { fontSize: 13, color: Colors.muted, lineHeight: 19 },
  privacy: { fontSize: 12, color: Colors.muted, lineHeight: 18 },
});
