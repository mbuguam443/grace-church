import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from 'expo-router';
import { useCallback, useRef, useState } from 'react';
import { FlatList, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { EmptyState, Loading } from '../components/ui';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { requestNotificationPermission } from '../lib/notifications';
import { Colors, Radius, Spacing } from '../lib/theme';
import { AppNotification } from '../lib/types';

const KIND_META: Record<string, { label: string; color: string; bg: string }> = {
  announcements: { label: 'Announcement', color: '#A8704A', bg: '#F0E3D3' },
  events: { label: 'Event', color: '#C9A227', bg: '#F7E9C3' },
  sermons: { label: 'Sermon', color: '#7E4F2D', bg: '#F0E3D3' },
  devotions: { label: 'Devotion', color: '#D97706', bg: '#FDEBD3' },
  'bible-study': { label: 'Bible Study', color: '#6F42C1', bg: '#F3EEFF' },
  songs: { label: 'Song', color: '#7E4F2D', bg: '#F0E3D3' },
  attendance: { label: 'Service', color: '#198754', bg: '#E4F5EA' },
};

const FALLBACK_META = { label: 'Update', color: Colors.navy, bg: Colors.navySoft };

function timeAgo(iso: string) {
  const then = new Date(iso).getTime();
  const diff = Date.now() - then;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(iso).toLocaleDateString('en-KE', { day: 'numeric', month: 'short' });
}

export default function NotificationsScreen() {
  const { token } = useAuth();
  const [items, setItems] = useState<AppNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const askedPermission = useRef(false);

  const load = useCallback(async (asRefresh = false) => {
    if (!token) return;
    if (asRefresh) setRefreshing(true);
    try {
      const res = await api.notifications(token);
      setItems(res.results);
      const unreadIds = res.results.filter((n) => !n.is_read).map((n) => n.id);
      if (unreadIds.length > 0) {
        api.markNotificationsRead(token, unreadIds).catch(() => undefined);
      }
    } catch {
      // list stays empty on failure
    } finally {
      setLoading(false);
      if (asRefresh) setRefreshing(false);
    }
  }, [token]);

  useFocusEffect(
    useCallback(() => {
      load();
      if (!askedPermission.current) {
        askedPermission.current = true;
        requestNotificationPermission();
      }
    }, [load]),
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.safe} edges={['top']}>
        <Loading />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => load(true)} tintColor={Colors.navy} />}
        ListEmptyComponent={<EmptyState icon="notifications-off-outline" text="No updates yet. We will let you know when something new is posted." />}
        renderItem={({ item }) => {
          const meta = KIND_META[item.kind] ?? FALLBACK_META;
          return (
            <View style={[styles.card, !item.is_read && styles.cardUnread]}>
              <View style={[styles.iconBox, { backgroundColor: meta.bg }]}>
                <Ionicons name="notifications-outline" size={20} color={meta.color} />
              </View>
              <View style={styles.cardBody}>
                <View style={styles.cardTitleRow}>
                  <View style={[styles.kindChip, { backgroundColor: meta.bg }]}>
                    <Text style={[styles.kindText, { color: meta.color }]}>{meta.label}</Text>
                  </View>
                  {!item.is_read ? <View style={styles.dot} /> : null}
                </View>
                <Text style={[styles.title, !item.is_read && styles.titleUnread]}>{item.title}</Text>
                {item.message ? (
                  <Text style={styles.message} numberOfLines={3}>
                    {item.message}
                  </Text>
                ) : null}
                <Text style={styles.time}>{timeAgo(item.created_at)}</Text>
              </View>
            </View>
          );
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  content: { padding: Spacing.lg, gap: Spacing.sm, flexGrow: 1 },
  card: {
    flexDirection: 'row',
    gap: Spacing.md,
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    padding: Spacing.md,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
  },
  cardUnread: {
    borderColor: Colors.navy,
    borderWidth: 1.5,
    backgroundColor: '#FFFFFF',
  },
  iconBox: {
    width: 40,
    height: 40,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardBody: { flex: 1, gap: Spacing.xs },
  cardTitleRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  kindChip: {
    alignSelf: 'flex-start',
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    borderRadius: 999,
  },
  kindText: { fontSize: 11, fontWeight: '700' },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.gold,
  },
  title: { fontSize: 15, fontWeight: '700', color: Colors.text },
  titleUnread: { fontWeight: '800', color: Colors.navy },
  message: { fontSize: 13, color: Colors.muted, lineHeight: 18 },
  time: { fontSize: 11, color: Colors.muted, fontWeight: '600', marginTop: 2 },
});