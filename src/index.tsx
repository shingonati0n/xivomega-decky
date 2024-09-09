 import {
  ButtonItem,
  DialogButton,
  ToggleField,
  Navigation,
  PanelSection,
  PanelSectionRow,
  staticClasses,
} from "@decky/ui";

import { 
  FunctionComponent, 
  useState,
  useEffect 
} from "react";

import { 
  BiTv 
} from "react-icons/bi";

import { 
  call,
  routerHook, 
  definePlugin 
} from "@decky/api";

function Content() {

const [enabled, setEnabled] = useState<boolean>(false);
//onClick behaviour
const onClick = async (e:boolean) => {
    call('set_enable', { enabled: e });
}

const initState = async() => {
  const getIsEnabledResponse:boolean= await call('is_enabled', {});
  setEnabled(getIsEnabledResponse as boolean);
}

useEffect(() => {
  initState();
},[]);
  return (
    <PanelSection title="Main Menu">
      <PanelSectionRow>
        <ToggleField 
        label="Latency Mitigation"
        checked={enabled}
        onChange={(e) => { setEnabled(e); onClick(e)}}/>
      </PanelSectionRow>
      <PanelSectionRow>
        <div>Enable to activate latency mitigation via podman container.</div>
      </PanelSectionRow>
      <PanelSectionRow>
        <div>Put True and False here</div>
      </PanelSectionRow>
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={() => {
            Navigation.Navigate("/decky-plugin-test");
            Navigation.CloseSideMenus();
          }}
        >
          Router
        </ButtonItem>
      </PanelSectionRow>
    </PanelSection>
  );
};

const DeckyPluginRouterTest: FunctionComponent = () => {
  return (
    <div style={{ marginTop: "50px", color: "white" }}>
      Hello World!
      <DialogButton onClick={() => Navigation.NavigateToLibraryTab()}>
        Go to Library
      </DialogButton>
    </div>
  );
};

export default definePlugin(() => {
  routerHook.addRoute("/decky-plugin-test", DeckyPluginRouterTest, {
    exact: true,
  });

  return {
    title: <div className={staticClasses.Title}>APIv2 Plugin</div>,
    content: <Content />,
    icon: <BiTv />,
    onDismount() {
      //serverApi.routerHook.removeRoute("/decky-plugin-test");
      console.log("Unloading");
    },
  };
});
