"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { LanguageProvider, useLanguage } from "@/context/LanguageContext";
import { ThemeProvider } from "@/context/ThemeContext";
import { SidebarProvider } from "@/context/SidebarContext";

function GoogleOAuthProviderWithLocale({ children }: { children: React.ReactNode }) {
  const { lang } = useLanguage();
  const locale = lang === "kk" ? "kk" : lang === "en" ? "en" : "ru";
  return (
    <GoogleOAuthProvider
      clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ""}
      locale={locale}
    >
      {children}
    </GoogleOAuthProvider>
  );
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Оптимизированное кеширование для улучшения производительности
            staleTime: 5 * 60 * 1000, // Данные считаются свежими 5 минут (300000ms)
            gcTime: 10 * 60 * 1000, // Храним данные в кеше 10 минут (600000ms)
            refetchOnMount: false, // Используем кеш при монтировании, если данные свежие
            refetchOnWindowFocus: false, // Не обновляем при фокусе окна
            refetchOnReconnect: true, // Обновляем при восстановлении соединения
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <LanguageProvider>
          <GoogleOAuthProviderWithLocale>
            <SidebarProvider>{children}</SidebarProvider>
          </GoogleOAuthProviderWithLocale>
        </LanguageProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
