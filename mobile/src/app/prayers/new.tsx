import { useRouter } from 'expo-router';
import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Switch, Text, View } from 'react-native';

import { Btn, Field } from '../../components/ui';
import { useAuth } from '../../lib/auth';
import { api } from '../../lib/api';
import { PRAYER_CATEGORIES } from '../../lib/library';
import { Colors, Radius, Spacing } from '../../lib/theme';

export default function NewPrayerScreen() {
  const { token } = useAuth();
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [request, setRequest] = useState('');
  const [category, setCategory] = useState('other');
  const [confidential, setConfidential] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    if (!token) return;
    if (!title.trim() || !request.trim()) {
      setError('Please provide both a title and the prayer request.');
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await api.createPrayer(token, {
        title: title.trim(),
        request: request.trim(),
        category,
        is_confidential: confidential,
      });
      router.back();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not submit request.');
      setBusy(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
      <Text style={styles.intro}>
        Share a prayer need with our prayer team. You can mark it as confidential so only the pastors see it.
      </Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <Field label="Title" value={title} onChangeText={setTitle} placeholder="e.g. Healing for my mother" placeholderTextColor={Colors.muted} />
      <Field
        label="Prayer request"
        value={request}
        onChangeText={setRequest}
        placeholder="Write your request here…"
        placeholderTextColor={Colors.muted}
        multiline
        numberOfLines={5}
        style={styles.textArea}
      />

      <Text style={styles.label}>Category</Text>
      <View style={styles.chips}>
        {PRAYER_CATEGORIES.map((c) => {
          const active = category === c.value;
          return (
            <Pressable
              key={c.value}
              onPress={() => setCategory(c.value)}
              style={[styles.chip, active && styles.chipActive]}>
              <Text style={[styles.chipText, active && styles.chipTextActive]}>{c.label}</Text>
            </Pressable>
          );
        })}
      </View>

      <View style={styles.switchRow}>
        <View style={styles.switchText}>
          <Text style={styles.switchTitle}>Confidential</Text>
          <Text style={styles.switchHint}>Only the pastoral team can see this request.</Text>
        </View>
        <Switch
          value={confidential}
          onValueChange={setConfidential}
          trackColor={{ false: Colors.border, true: Colors.navy }}
        />
      </View>

      <Btn title={busy ? 'Submitting…' : 'Submit Request'} onPress={submit} loading={busy} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: Spacing.lg, gap: Spacing.lg, backgroundColor: Colors.bg },
  intro: { fontSize: 14, color: Colors.muted, lineHeight: 20 },
  error: { color: Colors.danger, fontSize: 13 },
  textArea: { minHeight: 110, textAlignVertical: 'top' },
  label: { fontSize: 13, fontWeight: '600', color: Colors.muted },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  chip: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: Radius.md,
    backgroundColor: Colors.card,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  chipActive: { backgroundColor: Colors.navy, borderColor: Colors.navy },
  chipText: { fontSize: 13, fontWeight: '600', color: Colors.text },
  chipTextActive: { color: '#FFF' },
  switchRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: Spacing.md },
  switchText: { flex: 1, gap: 2 },
  switchTitle: { fontSize: 15, fontWeight: '700', color: Colors.text },
  switchHint: { fontSize: 12, color: Colors.muted },
});