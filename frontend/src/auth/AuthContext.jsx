import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  ApiError,
  clearAccessToken,
  getAccessToken,
  getCurrentUser,
  logout as logoutRequest,
  verifyLoginOtp,
} from "../services/api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState(() =>
    getAccessToken() ? "loading" : "unauthenticated",
  );
  const [authError, setAuthError] = useState("");

  useEffect(() => {
    const handleUnauthorized = () => {
      clearAccessToken();
      setUser(null);
      setStatus("unauthenticated");
      setAuthError("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
    };
    globalThis.addEventListener?.("seatsense:unauthorized", handleUnauthorized);
    let active = true;
    if (!getAccessToken()) {
      return () => {
        active = false;
        globalThis.removeEventListener?.(
          "seatsense:unauthorized",
          handleUnauthorized,
        );
      };
    }

    getCurrentUser()
      .then((profile) => {
        if (active) {
          setUser(profile);
          setStatus("authenticated");
        }
      })
      .catch((error) => {
        if (!active) return;
        if (error instanceof ApiError && error.status === 401) {
          clearAccessToken();
        } else {
          setAuthError(error.message);
        }
        setStatus("unauthenticated");
      });

    return () => {
      active = false;
      globalThis.removeEventListener?.(
        "seatsense:unauthorized",
        handleUnauthorized,
      );
    };
  }, []);

  const login = useCallback(async (email, otp) => {
    const profile = await verifyLoginOtp(email, otp);
    setUser(profile);
    setAuthError("");
    setStatus("authenticated");
  }, []);

  const signOut = useCallback(async () => {
    try {
      if (getAccessToken()) await logoutRequest();
    } finally {
      clearAccessToken();
      setUser(null);
      setStatus("unauthenticated");
    }
  }, []);

  const value = useMemo(
    () => ({ user, status, authError, login, signOut }),
    [user, status, authError, login, signOut],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
