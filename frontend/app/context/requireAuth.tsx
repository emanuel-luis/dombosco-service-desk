"use client";

import React, { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { getToken } from "../lib/client";

const PUBLIC_PATHS = ["/login", "/createAccount", "/api/auth/callback"];

const RequireAuth: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!PUBLIC_PATHS.includes(pathname) && !getToken()) {
      router.push("/login");
    }
  }, [router, pathname]);

  return <>{children}</>;
};

export default RequireAuth;
