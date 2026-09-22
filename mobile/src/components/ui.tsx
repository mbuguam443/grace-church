import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, TextInputProps, View } from 'react-native';

import { Colors, Radius, Spacing } from '../lib/theme';

export function Card({ children, style }: { children: React.ReactNode; style?: object }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function Row({ children, style }: { children: React.ReactNode; style?: object }) {
  return <View style={[styles.row, style]}>{children}</View>;
}

export function Chip({
  label,
  color = Colors.navy,
  bg = Colors.goldLight,
}: {
  label: string;
  color?: string;
  bg?: string;
}) {
  return (
    <View style={[styles.chip, { backgroundColor: bg }]}>
      <Text style={[styles.chipText, { color }]} numberOfLines={1}>
        {label}
      </Text>
    </View>
  );
}

type BtnVariant = 'primary' | 'outline' | 'danger';

export function Btn({
  title,
  onPress,
  variant = 'primary',
  loading = false,
  disabled = false,
  style,
}: {
  title: string;
  onPress: () => void;
  variant?: BtnVariant;
  loading?: boolean;
  disabled?: boolean;
  style?: object;
}) {
  const palettes: Record<BtnVariant, { bg: string; fg: string; border?: string }> = {
    primary: { bg: Colors.navy, fg: '#FFF' },
    outline: { bg: 'transparent', fg: Colors.navy, border: Colors.navy },
    danger: { bg: Colors.danger, fg: '#FFF' },
  };
  const p = palettes[variant];
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      style={({ pressed }) => [
        styles.btn,
        { backgroundColor: p.bg, borderColor: p.border ?? 'transparent', opacity: disabled ? 0.55 : 1 },
        style,
        pressed && styles.btnPressed,
      ]}>
      {loading ? <ActivityIndicator color={p.fg} /> : <Text style={[styles.btnText, { color: p.fg }]}>{title}</Text>}
    </Pressable>
  );
}

export function Field({
  label,
  secure = false,
  ...props
}: TextInputProps & { label: string; secure?: boolean }) {
  const [hidden, setHidden] = useState(secure);
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.inputWrap}>
        <TextInput
          placeholderTextColor={Colors.muted}
          {...props}
          secureTextEntry={secure ? hidden : undefined}
          style={[styles.input, secure && styles.inputSecure, props.style]}
        />
        {secure && (
          <Pressable onPress={() => setHidden((v) => !v)} style={styles.eye} hitSlop={8}>
            <Ionicons name={hidden ? 'eye-off-outline' : 'eye-outline'} size={20} color={Colors.muted} />
          </Pressable>
        )}
      </View>
    </View>
  );
}

export function SectionTitle({ children }: { children: React.ReactNode }) {
  return <Text style={styles.sectionTitle}>{children}</Text>;
}

export function EmptyState({ icon, text }: { icon?: string; text: string }) {
  return (
    <View style={styles.empty}>
      {icon && <Ionicons name={icon as keyof typeof Ionicons.glyphMap} size={34} color={Colors.muted} />}
      <Text style={styles.emptyText}>{text}</Text>
    </View>
  );
}

export function Loading() {
  return (
    <View style={styles.centerFill}>
      <ActivityIndicator color={Colors.navy} size="large" />
    </View>
  );
}

export function ErrorBox({ text }: { text: string }) {
  return (
    <View style={[styles.centerFill, { padding: Spacing.xl }]}>
      <Ionicons name="cloud-offline-outline" size={34} color={Colors.danger} />
      <Text style={[styles.emptyText, { textAlign: 'center' }]}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  chip: {
    alignSelf: 'flex-start',
    paddingHorizontal: Spacing.sm + 2,
    paddingVertical: Spacing.xs,
    borderRadius: 999,
    maxWidth: '100%',
  },
  chipText: {
    fontSize: 12,
    fontWeight: '600',
  },
  btn: {
    height: 48,
    borderRadius: Radius.md,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    paddingHorizontal: Spacing.lg,
  },
  btnPressed: {
    opacity: 0.85,
  },
  btnText: {
    fontSize: 15,
    fontWeight: '700',
  },
  field: {
    gap: Spacing.sm,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: Colors.muted,
  },
  inputWrap: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: Radius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm + 4,
    fontSize: 15,
    color: Colors.text,
    backgroundColor: Colors.card,
  },
  inputSecure: {
    paddingRight: Spacing.xl + 8,
  },
  eye: {
    position: 'absolute',
    right: Spacing.md,
    padding: Spacing.xs,
    zIndex: 1,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: Colors.text,
    marginBottom: Spacing.sm,
  },
  empty: {
    alignItems: 'center',
    gap: Spacing.sm,
    paddingVertical: Spacing.xl,
  },
  emptyText: {
    color: Colors.muted,
    fontSize: 14,
  },
  centerFill: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: Spacing.md,
  },
});