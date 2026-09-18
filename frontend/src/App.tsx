import { AppProvider, useAppState } from "@/state/AppState";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { Onboarding } from "@/pages/Onboarding";
import { Home } from "@/pages/Home";
import { TwinProfile } from "@/pages/TwinProfile";
import { ScenarioBuilder } from "@/pages/ScenarioBuilder";
import { Loading } from "@/pages/Loading";
import { Results } from "@/pages/Results";
import { History } from "@/pages/History";

function MainApp() {
  const { view } = useAppState();

  return (
    <div className="max-w-[1180px] mx-auto px-7 pt-[22px] pb-[60px] border-l border-r border-line min-h-screen relative max-[860px]:px-4">
      <span className="absolute w-3.5 h-3.5 border border-line-strong top-2.5 left-2.5 border-r-0 border-b-0" />
      <span className="absolute w-3.5 h-3.5 border border-line-strong top-2.5 right-2.5 border-l-0 border-b-0" />
      <Nav />
      {view === "home" && <Home />}
      {view === "twin" && <TwinProfile />}
      {view === "scenario" && <ScenarioBuilder />}
      {view === "loading" && <Loading />}
      {view === "results" && <Results />}
      {view === "history" && <History />}
      <Footer />
    </div>
  );
}

function Shell() {
  const { view } = useAppState();
  if (view === "onboarding") return <Onboarding />;
  return <MainApp />;
}

export default function App() {
  return (
    <AppProvider>
      <Shell />
    </AppProvider>
  );
}
