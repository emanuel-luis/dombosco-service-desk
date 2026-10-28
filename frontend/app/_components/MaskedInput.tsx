"use client";

import * as React from "react";
import { applyMask, caretAfterDigits, digitsBefore, overflowsFullMask } from "../lib/mask";

type Props = React.InputHTMLAttributes<HTMLInputElement> & { mask: string };

// Plain input that reformats its value on change and keeps the caret on the same
// digit; works with Formik's field props.
export function MaskedInput({ mask, onChange, onKeyDown, ...props }: Props) {
  const ref = React.useRef<HTMLInputElement>(null);
  const pendingCaret = React.useRef<number | null>(null);

  // React may rewrite the DOM value on commit and reset the caret: set it again.
  React.useLayoutEffect(() => {
    if (pendingCaret.current !== null) {
      ref.current?.setSelectionRange(pendingCaret.current, pendingCaret.current);
      pendingCaret.current = null;
    }
  });

  return (
    <input
      inputMode="numeric"
      {...props}
      ref={ref}
      onKeyDown={(e) => {
        onKeyDown?.(e);
        const el = e.currentTarget;
        const { selectionStart: s, selectionEnd: end, value } = el;
        if (s === null || s !== end) return;
        // Caret next to a separator: move it beside the digit so the default
        // Backspace/Delete removes a digit instead of nothing.
        if (e.key === "Backspace" && s > 0 && /\D/.test(value[s - 1])) {
          const p = caretAfterDigits(value, digitsBefore(value, s), false);
          el.setSelectionRange(p, p);
        } else if (e.key === "Delete" && s < value.length && /\D/.test(value[s])) {
          const p = caretAfterDigits(value, digitsBefore(value, s));
          el.setSelectionRange(p, p);
        }
      }}
      onChange={(e) => {
        const el = e.target;
        const previous = String(props.value ?? "");
        const deleting = ((e.nativeEvent as InputEvent).inputType ?? "").startsWith("delete");
        if (!deleting && overflowsFullMask(previous, el.value, mask)) {
          // Full field: refuse the extra digit instead of pushing the last one out.
          const kept = Math.max(0, (el.selectionStart ?? 1) - 1);
          el.value = previous;
          el.setSelectionRange(kept, kept);
          return;
        }
        const n = digitsBefore(el.value, el.selectionStart ?? el.value.length);
        el.value = applyMask(el.value, mask);
        // Deleting keeps the caret before a separator. Some mobile keyboards report no usable
        // key on keydown, so this is the reliable place to decide it.
        const caret = caretAfterDigits(el.value, n, !deleting);
        el.setSelectionRange(caret, caret);
        pendingCaret.current = caret;
        onChange?.(e);
      }}
    />
  );
}
