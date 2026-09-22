import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect, useRouter } from 'expo-router';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Pressable, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Btn, Card, Chip, EmptyState, Loading, SectionTitle } from '../../components/ui';
import { useAuth } from '../../lib/auth';
import { api } from '../../lib/api';
import { presentLocalNotification, registerPushToken, setupNotificationChannel } from '../../lib/notifications';
import { Colors, formatDate, formatMoney, initials, Radius, Shadow, Spacing } from '../../lib/theme';
import { Announcement, ChurchEvent, ChurchService, PortalData } from '../../lib/types';

const FEATURED = [
  { kind: 'sermons', title: 'Sermons', subtitle: 'Notes & messages', icon: 'mic', color: '#A8704A', bg: '#F0E3D3' },
  { kind: 'bible-study', title: 'Bible Study', subtitle: 'Study notes', icon: 'book', color: '#6F42C1', bg: '#F3EEFF' },
  { kind: 'songs', title: 'Songs', subtitle: 'Hymns & lyrics', icon: 'musical-notes', color: '#7E4F2D', bg: '#F0E3D3' },
  { kind: 'prayers', title: 'Prayers', subtitle: 'Share a need', icon: 'hand-left', color: '#B5651D', bg: '#F7E6DC' },
];

export default function PortalScreen() {
  const { token, user, member, refresh } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<PortalData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const lastUnread = useRef<number | null>(null);

  useEffect(() => {
    if (token) {
      setupNotificationChannel();
      registerPushToken(token);
    }
  }, [token]);

  const load = useCallback(async () => {
    if (!token) return;
    try {
      const portal = await api.portal(token);
      setData(portal);
      setError(null);
      if (typeof portal.unread_count === 'number') setUnreadCount(portal.unread_count);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load portal.');
    }
  }, [token]);

  const pollNotifications = useCallback(async () => {
    if (!token) return;
    try {
      const res = await api.notifications(token);
      setUnreadCount(res.unread_count);
      if (lastUnread.current == null) {
        lastUnread.current = res.unread_count;
        return;
      }
      if (res.unread_count > lastUnread.current) {
        const fresh = res.results.find((n) => !n.is_read);
        if (fresh) {
          presentLocalNotification(fresh.title || 'New update from Grace Church Munyaka', fresh.message || 'Tap to read the latest update.');
        }
      }
      lastUnread.current = res.unread_count;
    } catch {
      // offline: leave badge as is
    }
  }, [token]);

  useFocusEffect(
    useCallback(() => {
      load();
      pollNotifications();
      const id = setInterval(pollNotifications, 60000);
      return () => clearInterval(id);
    }, [load, pollNotifications]),
  );

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await Promise.all([load(), refresh()]);
    setRefreshing(false);
  }, [load, refresh]);

  const today = new Date().toLocaleDateString('en-KE', { weekday: 'long', day: 'numeric', month: 'short' });

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.navy} />}>
        <View style={styles.hero}>
          <View style={styles.heroTopRow}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>{initials(user?.full_name)}</Text>
            </View>
            <View style={styles.heroText}>
              <Text style={styles.greeting}>Shalom,</Text>
              <Text style={styles.name}>{user?.full_name || 'Member'}</Text>
              <Text style={styles.subline}>
                {member ? `${member.member_number} · ${member.membership_status_label}` : user?.role_label}
              </Text>
            </View>
            <Pressable
              onPress={() => router.push('/notifications')}
              style={({ pressed }) => [styles.bell, pressed && styles.pressed]}
              hitSlop={8}>
              <Ionicons name="notifications-outline" size={22} color="#FFFFFF" />
              {unreadCount > 0 ? (
                <View style={styles.bellBadge}>
                  <Text style={styles.bellBadgeText}>{unreadCount > 9 ? '9+' : unreadCount}</Text>
                </View>
              ) : null}
            </Pressable>
          </View>
          <View style={styles.heroFooter}>
            <View style={styles.goldBar} />
            <Text style={styles.heroDate}>{today}</Text>
          </View>
        </View>

        {error && !data && <EmptyState icon="cloud-offline-outline" text={error} />}

        {data ? (
          <>
            <CheckInBanner services={data.today_services ?? []} token={token || ''} onDone={load} />
            <View style={styles.grid}>
              <StatTile
                icon="people-outline"
                label="Groups"
                value={data.counts.groups}
                tint="#A8704A"
                tintBg="#F0E3D3"
                onPress={() => router.push({ pathname: '/list/[kind]', params: { kind: 'groups' } })}
              />
              <StatTile
                icon="wallet-outline"
                label="Giving"
                value={formatMoney(data.counts.givings_total)}
                tint="#C9A227"
                tintBg="#F7E9C3"
                onPress={() => router.push({ pathname: '/list/[kind]', params: { kind: 'givings' } })}
              />
              <StatTile
                icon="calendar-outline"
                label="Attendance"
                value={data.counts.attendance}
                tint="#198754"
                tintBg="#E4F5EA"
                onPress={() => router.push({ pathname: '/list/[kind]', params: { kind: 'attendance' } })}
              />
              <StatTile
                icon="megaphone-outline"
                label="Events"
                value={data.counts.events}
                tint="#7E4F2D"
                tintBg="#F0E3D3"
                onPress={() => router.push({ pathname: '/list/[kind]', params: { kind: 'events' } })}
              />
            </View>

            <SectionTitle>Open to read</SectionTitle>
            <View style={styles.grid}>
              {FEATURED.map((m) => (
                <Pressable
                  key={m.kind}
                  onPress={() => router.push({ pathname: '/list/[kind]', params: { kind: m.kind } })}
                  style={({ pressed }) => [styles.featureTile, pressed && styles.pressed]}>
                  <View style={[styles.featureIcon, { backgroundColor: m.bg }]}>
                    <Ionicons name={m.icon as keyof typeof Ionicons.glyphMap} size={22} color={m.color} />
                  </View>
                  <Text style={styles.featureTitle}>{m.title}</Text>
                  <Text style={styles.featureSubtitle}>{m.subtitle}</Text>
                </Pressable>
              ))}
            </View>

            <UpcomingEvents events={data.events} onOpen={() => router.push({ pathname: '/list/[kind]', params: { kind: 'events' } })} />
            <Announcements
              items={data.announcements}
              onOpen={() => router.push({ pathname: '/list/[kind]', params: { kind: 'announcements' } })}
            />
          </>
        ) : !error ? (
          <Loading />
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

function CheckInBanner({
  services,
  token,
  onDone,
}: {
  services: ChurchService[];
  token: string;
  onDone: () => Promise<void>;
}) {
  const [busyId, setBusyId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  if (services.length === 0) return null;

  async function checkIn(id: number) {
    setBusyId(id);
    setError(null);
    try {
      await api.checkIn(token, id);
      await onDone();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not check in.');
    } finally {
      setBusyId(null);
    }
  }

  return (
    <View style={styles.block}>
      <SectionTitle>Today at church</SectionTitle>
      {error ? <Text style={styles.checkError}>{error}</Text> : null}
      {services.map((s) => (
        <Card key={s.id} style={styles.checkCard}>
          <View style={styles.checkRow}>
            <View style={styles.checkIcon}>
              <Ionicons name={s.checked_in ? 'checkmark-circle' : 'calendar'} size={22} color={s.checked_in ? Colors.success : Colors.navy} />
            </View>
            <View style={styles.rowText}>
              <Text style={styles.rowTitle}>{s.name}</Text>
              <Text style={styles.rowSubtitle}>
                {(s.start_time ? s.start_time.slice(0, 5) : 'Time TBA') + (s.location ? ` · ${s.location}` : '')}
              </Text>
            </View>
          </View>
          {s.checked_in ? (
            <Chip label="You're here" color={Colors.success} bg="#E4F5EA" />
          ) : s.can_check_in ? (
            <Btn title="I'm here — check in" loading={busyId === s.id} onPress={() => checkIn(s.id)} />
          ) : null}
        </Card>
      ))}
    </View>
  );
}

function StatTile({
  icon,
  label,
  value,
  tint,
  tintBg,
  onPress,
}: {
  icon: string;
  label: string;
  value: string | number;
  tint: string;
  tintBg: string;
  onPress: () => void;
}) {
  return (
    <Pressable onPress={onPress} style={({ pressed }) => [styles.tileWrap, pressed && styles.pressed]}>
      <Card style={styles.tile}>
        <View style={[styles.tileIcon, { backgroundColor: tintBg }]}>
          <Ionicons name={icon as keyof typeof Ionicons.glyphMap} size={18} color={tint} />
        </View>
        <Text style={styles.tileValue} numberOfLines={1} adjustsFontSizeToFit>
          {value}
        </Text>
        <Text style={styles.tileLabel}>{label}</Text>
      </Card>
    </Pressable>
  );
}

function UpcomingEvents({ events, onOpen }: { events: ChurchEvent[]; onOpen: () => void }) {
  if (events.length === 0) return null;
  return (
    <View style={styles.block}>
      <SectionTitle>Upcoming events</SectionTitle>
      {events.map((e) => (
        <Pressable key={e.id} onPress={onOpen} style={({ pressed }) => pressed && styles.pressed}>
          <Card style={styles.itemCard}>
            <View style={styles.eventRow}>
              <View style={styles.dateBadge}>
                <Text style={styles.dateDay}>{new Date(e.date).getDate()}</Text>
                <Text style={styles.dateMonth}>{new Date(e.date).toLocaleString('en-KE', { month: 'short' })}</Text>
              </View>
              <View style={styles.rowText}>
                <Text style={styles.rowTitle}>{e.name}</Text>
                <Text style={styles.rowSubtitle}>
                  {e.location || 'GC'} · {formatDate(e.date)}
                </Text>
              </View>
              <Chip label={e.registered ? 'Registered' : 'Open'} />
            </View>
          </Card>
        </Pressable>
      ))}
    </View>
  );
}

function Announcements({ items, onOpen }: { items: Announcement[]; onOpen: () => void }) {
  if (items.length === 0) return null;
  return (
    <View style={styles.block}>
      <SectionTitle>Announcements</SectionTitle>
      {items.map((a) => (
        <Pressable key={a.id} onPress={onOpen} style={({ pressed }) => pressed && styles.pressed}>
          <Card style={styles.itemCard}>
            <Text style={styles.rowTitle}>{a.title}</Text>
            <Text style={styles.rowSubtitle} numberOfLines={2}>
              {a.message}
            </Text>
            <Text style={styles.dateLine}>{formatDate(a.publish_date)}</Text>
          </Card>
        </Pressable>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  content: { padding: Spacing.lg, paddingBottom: Spacing.xl, gap: Spacing.lg },
  hero: {
    backgroundColor: Colors.navy,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
  },
  heroTopRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  bell: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.18)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.35)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  bellBadge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: Colors.gold,
    borderRadius: 999,
    minWidth: 18,
    height: 18,
    paddingHorizontal: 4,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: '#FFFFFF',
  },
  bellBadgeText: { color: '#FFFFFF', fontSize: 10, fontWeight: '800' },
  avatar: {
    width: 54,
    height: 54,
    borderRadius: 27,
    backgroundColor: 'rgba(255,255,255,0.18)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.35)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: { color: '#FFF', fontSize: 20, fontWeight: '800' },
  heroText: { flex: 1, gap: 1 },
  greeting: { fontSize: 13, color: 'rgba(255,255,255,0.85)', fontWeight: '700' },
  name: { fontSize: 22, fontWeight: '900', color: '#FFFFFF' },
  subline: { fontSize: 12, color: 'rgba(255,255,255,0.8)', marginTop: 2 },
  heroFooter: { marginTop: Spacing.md, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  goldBar: { height: 3, width: 64, borderRadius: 999, backgroundColor: Colors.gold },
  heroDate: { fontSize: 12, color: 'rgba(255,255,255,0.8)', fontWeight: '600' },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  tileWrap: { width: '48%', flexGrow: 1 },
  tile: { gap: Spacing.xs, minHeight: 96 },
  tileIcon: {
    width: 34,
    height: 34,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tileValue: { fontSize: 16, fontWeight: '900', color: Colors.navy, marginTop: Spacing.xs },
  tileLabel: { fontSize: 12, color: Colors.muted, fontWeight: '600' },
  featureTile: {
    width: '48%',
    flexGrow: 1,
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    padding: Spacing.md,
    gap: Spacing.sm,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
    minHeight: 118,
    ...Shadow,
  },
  featureIcon: {
    width: 42,
    height: 42,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  featureTitle: { fontSize: 15, fontWeight: '800', color: Colors.text },
  featureSubtitle: { fontSize: 12, color: Colors.muted },
  block: { gap: Spacing.sm },
  itemCard: { gap: Spacing.xs },
  checkCard: { gap: Spacing.md },
  checkRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  checkIcon: {
    width: 42,
    height: 42,
    borderRadius: 12,
    backgroundColor: Colors.navySoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkError: { color: Colors.danger, fontSize: 13, fontWeight: '600' },
  pressed: { opacity: 0.75 },
  rowText: { flex: 1 },
  rowTitle: { fontSize: 15, fontWeight: '700', color: Colors.text },
  rowSubtitle: { fontSize: 13, color: Colors.muted, marginTop: 1 },
  eventRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  dateBadge: {
    width: 48,
    height: 48,
    borderRadius: Radius.md,
    backgroundColor: Colors.goldLight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dateDay: { fontSize: 16, fontWeight: '900', color: Colors.navy },
  dateMonth: { fontSize: 10, fontWeight: '700', color: Colors.muted, textTransform: 'capitalize' },
  dateLine: { fontSize: 12, color: Colors.muted, marginTop: Spacing.xs },
});
