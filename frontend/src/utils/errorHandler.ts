export interface ApiError {
  code: string;
  message: string;
  retryAfter?: number;
}

export function parseApiError(status: number, body?: Record<string, unknown>): ApiError {
  if (status === 429) {
    return {
      code: "rate_limit",
      message: (body?.message as string) || "Слишком много запросов. Подожди немного.",
      retryAfter: (body?.retry_after as number) || 60,
    };
  }
  if (status === 401) {
    return { code: "unauthorized", message: "Сессия истекла. Войди снова." };
  }
  if (status === 402) {
    return { code: (body?.detail as string) || "FREE_LIMIT_REACHED", message: "Нужна подписка Pro" };
  }
  if (status >= 500) {
    return { code: "server_error", message: "Сервер недоступен, попробуй позже." };
  }
  return {
    code: "error",
    message: (body?.message as string) || (body?.detail as string) || "Ошибка. Попробуй ещё раз.",
  };
}

export function parseNetworkError(): ApiError {
  return { code: "network", message: "Нет соединения с сервером." };
}

export function parseStreamError(data: Record<string, unknown>): ApiError | null {
  if (data.error) {
    return {
      code: data.error as string,
      message: (data.message as string) || "Ошибка AI сервиса",
    };
  }
  return null;
}
