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
  //ServerAPI,
  //showContextMenu,

  staticClasses,
} from "@decky/ui";
import { VFC, useState } from "react";
import { BiTv } from "react-icons/bi";

//import logo from "../assets/logo.png";
import { routerHook } from "@decky/api";

function Content() {
const [_result, setResult] = useState<string| undefined>();
const onChange = async () => {
  const result = "bla";
  setResult(result);
};
  return (
    <PanelSection title="Main Menu">
      <PanelSectionRow>
        <ToggleField 
        label="Latency Mitigation"
        tooltip="Enable to activate latency mitigation via podman container" 
        highlightOnFocus={true}
        disabled={false} 
        checked={true}
        onChange={() => {onChange()}}/>
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
