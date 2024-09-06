import {
  ButtonItem,
  definePlugin,
  DialogButton,
  ToggleField,
  //Menu,
  //MenuItem,
  Navigation,
  PanelSection,
  PanelSectionRow,
  ServerAPI,
  //showContextMenu,
  staticClasses,
} from "decky-frontend-lib";
import { VFC,useState } from "react";
import { BiTv } from "react-icons/bi";

import logo from "../assets/logo.png";


interface AddMethodArgs {
  left: number;
  right: number;
}

const Content: VFC<{ serverAPI: ServerAPI }> = ({serverAPI}) => {
const [_result, setResult] = useState<number | undefined>();

/* tslint:disable:no-unused-variable */
const onClick = async () => {
  const result = await serverAPI.callPluginMethod<AddMethodArgs, number>(
    "add",
    {
      left: 2,
      right: 2,
    }
  );
  if (result.success) {
    setResult(result.result);
  }
};

onClick()

  return (
    <PanelSection title="Main Menu">
      <PanelSectionRow>
        <ToggleField 
        label="Latency Mitigation"
        tooltip="Enable to activate latency mitigation via podman container" 
        disabled={true} 
        checked={false}/>
      </PanelSectionRow>
      <PanelSectionRow>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <img src={logo} />
        </div>
      </PanelSectionRow>
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={() => {
            Navigation.CloseSideMenus();
            Navigation.Navigate("/decky-plugin-test");
          }}
        >
          Router
        </ButtonItem>
      </PanelSectionRow>
    </PanelSection>
  );
};

const DeckyPluginRouterTest: VFC = () => {
  return (
    <div style={{ marginTop: "50px", color: "white" }}>
      Hello World!
      <DialogButton onClick={() => Navigation.NavigateToLibraryTab()}>
        Go to Library
      </DialogButton>
    </div>
  );
};

export default definePlugin((serverApi: ServerAPI) => {
  serverApi.routerHook.addRoute("/decky-plugin-test", DeckyPluginRouterTest, {
    exact: true,
  });

  return {
    title: <div className={staticClasses.Title}>Example Plugin</div>,
    content: <Content serverAPI={serverApi} />,
    icon: <BiTv />,
    onDismount() {
      serverApi.routerHook.removeRoute("/decky-plugin-test");
    },
  };
});
