"use client";

import * as React from "react";
import { applyMask } from "../lib/mask";

type Props = React.InputHTMLAttributes<HTMLInputElement> & { mask: string };

// Plain input that reformats its value on change; works with Formik's field props.
export function MaskedInput({ mask, onChange, ...props }: Props) {
  return (
    <input
      {...props}
      onChange={(e) => {
        e.target.value = applyMask(e.target.value, mask);
        onChange?.(e);
      }}
    />
  );
}
