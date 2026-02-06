import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { LogIn } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";

const Login = () => {
  const navigate = useNavigate();
  const { isAuthenticated, login, loading, error } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-6">
      <Card className="w-full max-w-md border-border bg-card shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">Sign in to Company Q&A</CardTitle>
          <p className="text-sm text-muted-foreground">
            Use Google single sign-on to access chat and documents.
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            className="w-full gap-2"
            onClick={() => void login()}
            disabled={loading}
          >
            <LogIn className="h-4 w-4" />
            {loading ? "Checking..." : "Sign in with Google"}
          </Button>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <p className="text-xs text-muted-foreground">
            After signing in, you’ll be redirected back to the app.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;
