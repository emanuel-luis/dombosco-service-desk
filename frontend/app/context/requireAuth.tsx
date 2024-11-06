"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import useLoginValidation from "../utils/loginValidation";

const RequireAuth: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const router = useRouter();
  useLoginValidation()
  
  useEffect(() => {
    const getCookie = (name: string) => {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(";").shift();
    };

    const tokenFromLocalStorage = localStorage.getItem("token");
    const tokenFromCookies = getCookie("token");

    if (!tokenFromLocalStorage && !tokenFromCookies) {
      router.push("/login");
    }
  }, [router]);

  return <>{children}</>;
};

export default RequireAuth;
