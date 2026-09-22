import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { MODULES, ModuleMeta } from '../../lib/library';
import { Colors, Radius, Shadow, Spacing } from '../../lib/theme';

const GROUPS: { title: string; kinds: string[] }[] = [
  { title: 'The Word', kinds: ['sermons', 'bible-study', 'devotions'] },
  { title: 'Worship', kinds: ['songs'] },
  { title: 'My records', kinds: ['groups', 'givings', 'attendance', 'prayers'] },
  { title: 'Church life', kinds: ['events', 'announcements'] },
];

const ACCENT: Record<string, { color: string; bg: string }> = {
  sermons: { color: '#A8704A', bg: '#F0E3D3' },
  'bible-study': { color: '#6F42C1', bg: '#F3EEFF' },
  devotions: { color: '#D97706', bg: '#FEF3C7' },
  songs: { color: '#7E4F2D', bg: '#F0E3D3' },
  groups: { color: '#A8704A', bg: '#F0E3D3' },
  givings: { color: '#C9A227', bg: '#F7E9C3' },
  attendance: { color: '#198754', bg: '#E4F5EA' },
  prayers: { color: '#B5651D', bg: '#F7E6DC' },
  events: { color: '#7E4F2D', bg: '#F0E3D3' },
  announcements: { color: '#8A7763', bg: '#F1EADD' },
};

export default function LibraryScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>Library</Text>
        <Text style={styles.subtitle}>Sermons, songs, groups and your church records</Text>

        {GROUPS.map((group) => {
          const items = group.kinds
            .map((kind) => MODULES.find((m) => m.kind === kind))
            .filter((m): m is ModuleMeta => Boolean(m));
          return (
            <View key={group.title} style={styles.section}>
              <Text style={styles.sectionTitle}>{group.title}</Text>
              <View style={styles.grid}>
                {items.map((m) => {
                  const accent = ACCENT[m.kind] ?? { color: Colors.navy, bg: Colors.navySoft };
                  const wide = items.length === 1;
                  return (
                    <Pressable
                      key={m.kind}
                      onPress={() => router.push({ pathname: '/list/[kind]', params: { kind: m.kind } })}
                      style={({ pressed }) => [
                        styles.tile,
                        wide && styles.tileWide,
                        pressed && styles.pressed,
                      ]}>
                      <View style={[styles.iconBox, { backgroundColor: accent.bg }]}>
                        <Ionicons name={m.icon as keyof typeof Ionicons.glyphMap} size={22} color={accent.color} />
                      </View>
                      <Text style={styles.tileTitle}>{m.title}</Text>
                      <Text style={styles.tileSubtitle} numberOfLines={2}>
                        {m.subtitle}
                      </Text>
                    </Pressable>
                  );
                })}
              </View>
            </View>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  content: { padding: Spacing.lg, paddingBottom: Spacing.xl, gap: Spacing.lg },
  title: { fontSize: 28, fontWeight: '900', color: Colors.navy },
  subtitle: { fontSize: 14, color: Colors.muted, marginTop: -Spacing.md },
  section: { gap: Spacing.sm },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: Colors.text,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  tile: {
    width: '48%',
    flexGrow: 1,
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    padding: Spacing.md,
    gap: Spacing.sm,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
    minHeight: 132,
    ...Shadow,
  },
  tileWide: { width: '100%' },
  pressed: { opacity: 0.75 },
  iconBox: {
    width: 44,
    height: 44,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tileTitle: { fontSize: 16, fontWeight: '800', color: Colors.text },
  tileSubtitle: { fontSize: 12, color: Colors.muted, lineHeight: 17 },
});
