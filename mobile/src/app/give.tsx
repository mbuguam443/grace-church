import { Ionicons } from '@expo/vector-icons';
import { Stack, router } from 'expo-router';
import { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';

import { Btn, Card, Field } from '../components/ui';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Colors, formatMoney, Radius, Spacing } from '../lib/theme';

const CATEGORIES: { key: string; label: string; hint: string }[] = [
  { key: 'tithe', label: 'Tithe', hint: '10% of your income' },
  { key: 'offering', label: 'Offering', hint: 'Freewill offering' },
  { key: 'donation', label: 'Donation', hint: 'A general gift' },
  { key: 'building_fund', label: 'Building Fund', hint: 'Towards our church building' },
  { key: 'missions', label: 'Missions', hint: 'Support for ministry' },
  { key: 'special_contribution', label: 'Special Contribution', hint: 'A specific project' },
  { key: 'other', label: 'Other', hint: 'Something else' },
];

const FREQUENCIES: { key: string; label: string }[] = [
  { key: 'one_time', label: 'One-time' },
  { key: 'monthly', label: 'Monthly' },
  { key: 'annual', label: 'Annually' },
];

const QUICK = ['500', '1000', '2000', '5000'];

export default function GiveScreen() {
  const { token } = useAuth();
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('tithe');
  const [frequency, setFrequency] = useState('one_time');
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const amountError = (() => {
    if (!amount.trim()) return null;
    const value = Number(amount);
    if (!Number.isFinite(value)) return 'Enter a valid amount.';
    if (value <= 0) return 'The amount must be more than zero.';
    if (value > 9_999_999_999) return 'That amount is too large.';
    return null;
  })();

  async function submit() {
    if (!token) return;
    if (!amount.trim() || amountError) return;
    setBusy(true);
    setError(null);
    try {
      await api.give(token, { amount: amount.trim(), giving_category: category, frequency, note: note.trim() });
      setAmount('');
      setNote('');
      setFrequency('one_time');
      router.back();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not submit your giving. Please try again.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={styles.safe}>
      <Stack.Screen options={{ title: 'Give', headerShadowVisible: false }} />
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.flex}>
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
          <View style={styles.hero}>
            <Ionicons name="heart" size={18} color={Colors.gold} />
            <Text style={styles.heroTitle}>Thank you for giving</Text>
            <Text style={styles.heroSub}>Your giving is recorded as pending until the finance team confirms it.</Text>
            <View style={styles.goldBar} />
          </View>

          <View style={styles.body}>
            <View style={styles.amountBox}>
              <Text style={styles.currency}>KSh</Text>
              <TextInput
                value={amount}
                onChangeText={(v: string) => setAmount(v.replace(/[^0-9.]/g, ''))}
                placeholder="0"
                placeholderTextColor={Colors.border}
                keyboardType="decimal-pad"
                style={styles.amountInput}
              />
            </View>
            {amountError ? <Text style={styles.error}>{amountError}</Text> : null}

            <View style={styles.quickRow}>
              {QUICK.map((value) => (
                <Pressable
                  key={value}
                  onPress={() => setAmount(value)}
                  style={[styles.quick, amount === value && styles.quickActive]}
                >
                  <Text style={[styles.quickText, amount === value && styles.quickTextActive]}>{formatMoney(value)}</Text>
                </Pressable>
              ))}
            </View>

            <View style={styles.group}>
              <Text style={styles.groupLabel}>What is this for?</Text>
              {CATEGORIES.map((c) => {
                const active = category === c.key;
                return (
                  <Pressable key={c.key} onPress={() => setCategory(c.key)} style={[styles.option, active && styles.optionActive]}>
                    <View style={styles.optionText}>
                      <Text style={styles.optionLabel}>{c.label}</Text>
                      <Text style={styles.optionHint}>{c.hint}</Text>
                    </View>
                    <Ionicons
                      name={active ? 'radio-button-on' : 'radio-button-off'}
                      size={20}
                      color={active ? Colors.gold : Colors.border}
                    />
                  </Pressable>
                );
              })}
            </View>

            <View style={styles.group}>
              <Text style={styles.groupLabel}>How often?</Text>
              <View style={styles.chipRow}>
                {FREQUENCIES.map((f) => {
                  const active = frequency === f.key;
                  return (
                    <Pressable key={f.key} onPress={() => setFrequency(f.key)} style={[styles.pill, active && styles.pillActive]}>
                      <Text style={[styles.pillText, active && styles.pillTextActive]}>{f.label}</Text>
                    </Pressable>
                  );
                })}
              </View>
            </View>

            <Field
              label="Note (optional)"
              value={note}
              onChangeText={setNote}
              placeholder="Anything the finance team should know"
              multiline
              style={styles.note}
            />

            {error ? <Text style={styles.error}>{error}</Text> : null}

            <Btn
              title={amount.trim() ? `Give ${formatMoney(amount)}` : 'Give'}
              loading={busy}
              disabled={!amount.trim() || !!amountError}
              onPress={submit}
            />
            <Card style={styles.footNote}>
              <Text style={styles.footText}>
                Giving records appear under “Give” and “Giving History” once they are confirmed.
              </Text>
            </Card>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  flex: { flex: 1 },
  scroll: { paddingBottom: Spacing.xl },
  hero: { backgroundColor: Colors.navy, paddingHorizontal: Spacing.lg, paddingVertical: Spacing.xl, gap: Spacing.sm },
  heroTitle: { fontSize: 22, fontWeight: '900', color: '#FFF' },
  heroSub: { fontSize: 13, color: 'rgba(255,255,255,0.8)', lineHeight: 19 },
  goldBar: { marginTop: Spacing.sm, height: 3, width: 56, borderRadius: 999, backgroundColor: Colors.gold },
  body: { padding: Spacing.lg, gap: Spacing.lg },
  amountBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    paddingHorizontal: Spacing.lg,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
  },
  currency: { fontSize: 20, fontWeight: '800', color: Colors.muted },
  amountInput: {
    flex: 1,
    fontSize: 32,
    fontWeight: '900',
    color: Colors.text,
    paddingVertical: Spacing.lg,
  },
  error: { fontSize: 13, fontWeight: '700', color: Colors.danger },
  quickRow: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  quick: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    borderRadius: 999,
    backgroundColor: Colors.card,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
  },
  quickActive: { backgroundColor: Colors.navy, borderColor: Colors.navy },
  quickText: { fontSize: 13, fontWeight: '800', color: Colors.text },
  quickTextActive: { color: '#FFF' },
  group: { gap: Spacing.sm },
  groupLabel: { fontSize: 12, fontWeight: '800', color: Colors.muted, textTransform: 'uppercase', letterSpacing: 0.4 },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
    backgroundColor: Colors.card,
    borderRadius: Radius.md,
    padding: Spacing.md,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
  },
  optionActive: { borderColor: Colors.gold, backgroundColor: Colors.goldLight },
  optionText: { flex: 1, gap: 2 },
  optionLabel: { fontSize: 15, fontWeight: '700', color: Colors.text },
  optionHint: { fontSize: 12, color: Colors.muted },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  pill: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    borderRadius: 999,
    backgroundColor: Colors.card,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
  },
  pillActive: { backgroundColor: Colors.navy, borderColor: Colors.navy },
  pillText: { fontSize: 13, fontWeight: '700', color: Colors.text },
  pillTextActive: { color: '#FFF' },
  note: { minHeight: 88, textAlignVertical: 'top' },
  footNote: { backgroundColor: Colors.goldLight, borderWidth: 0 },
  footText: { fontSize: 12, color: Colors.text, lineHeight: 18 },
});
