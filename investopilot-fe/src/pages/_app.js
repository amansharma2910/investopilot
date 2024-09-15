import "../styles/globals.css";
import React, { useEffect, useState } from 'react';
import App from 'next/app';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import SuperTokens, { SuperTokensWrapper } from 'supertokens-auth-react';
import { getSuperTokensRoutesForReactRouterDom } from 'supertokens-auth-react/ui';
import * as reactRouterDom from 'react-router-dom';
import Session from 'supertokens-auth-react/recipe/session';
import EmailPassword from "supertokens-auth-react/recipe/emailpassword";
import { EmailPasswordPreBuiltUI } from 'supertokens-auth-react/recipe/emailpassword/prebuiltui';


const MyApp = ({ Component, pageProps }) => {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      SuperTokens.init({
        appInfo: {
            appName: "InvestoPilot",
            apiDomain: "http://localhost:8000",
            websiteDomain: "http://localhost:3000",
            apiBasePath: "/auth",
            websiteBasePath: "/auth"
        },
        recipeList:[
          EmailPassword.init(),
          Session.init()
        ]
      });
      setIsClient(true);
    }
  }, []);

  if (!isClient) {
    return null;
  }

  return (
    <SuperTokensWrapper>
      <BrowserRouter>
        <Routes>
          {/* This renders the login UI on the /auth route */}
          {getSuperTokensRoutesForReactRouterDom(reactRouterDom, [EmailPasswordPreBuiltUI])}
          {/* Your app routes */}
          <Route path="/auth/*" element={<Component {...pageProps} />} />
          <Route path="/" element={<ProtectedRoute />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </SuperTokensWrapper>
  );
};

const ProtectedRoute = ({ Component, pageProps }) => {
  const [loading, setLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    async function checkSession() {
      const sessionExists = await Session.doesSessionExist();
      if (sessionExists) {
        const userId = await Session.getUserId();
        setIsLoggedIn(true);
        setUserId(userId);
      } else {
        setIsLoggedIn(false);
      }
      setLoading(false);
    }
    checkSession();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isLoggedIn) {
    return <Navigate to="/auth" />;
  }

  return <LoggedInPage email={userId} />;
};

const LoggedInPage = ({ email }) => {
  return <div>You are logged in as {email}</div>;
};

// Ensure getInitialProps is handled correctly
MyApp.getInitialProps = async (appContext) => {
  const appProps = await App.getInitialProps(appContext);
  return { ...appProps };
};

export default MyApp;