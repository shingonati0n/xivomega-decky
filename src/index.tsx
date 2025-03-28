import {
	PanelSection,
	PanelSectionRow,
	ToggleField,
	Spinner,
	staticClasses,
	ButtonItem,
	Navigation,
	showContextMenu,
	Menu,
	MenuItem,
	Router
} from "@decky/ui";

import {
	addEventListener,
	removeEventListener,
	call,
	definePlugin,
	routerHook
} from "@decky/api"

import { useLocalStorage } from "./useLocalStorage";
import { useEffect } from "react";
import { GiCagedBall,GiOmega } from 'react-icons/gi'
import { AiFillGithub, AiFillHeart,AiOutlineRightSquare, AiOutlineSetting } from "react-icons/ai";
import { LogRouter } from "./pages/log";
import { OpcodeRouter } from "./pages/opcodes";
import { SettingsRouter } from "./pages/settings";

import logo from "../assets/XIVOmegaLogo.png";
import qrc from "../assets/qr_code.png";


const onKill = async() => {call('stop_status')}

const xivOmegaSessionClear = async() => {
		// Clear any saved state and cached data from previous sessions
		localStorage.removeItem("checkd");
		localStorage.removeItem("loading");
		localStorage.removeItem("storagep");
		localStorage.removeItem("ctx");
		localStorage.removeItem("wlan");
		localStorage.removeItem("thisIp");
  };
//Run before anything on startup
xivOmegaSessionClear();

function Content() {
	const textStyle = {fontSize: "11px"};
	const [checkd, setCheckd] = useLocalStorage("checkd",false);
	const [loading,setLoading] = useLocalStorage("loading",false);
	const [storagep,setStoragep] = useLocalStorage("storagep",false);
	const [ctx,setCtx] = useLocalStorage("ctx",false);
	const [wlan,setWlan] = useLocalStorage("wlan",false);
	const [thisIp,setCurrIp] = useLocalStorage("thisIp","");


	function enableToggle() {
		setLoading(false);
	};

	function disableToggle() {
		setLoading(true);
	};

	function storageConfError() {
		setStoragep(true);
	};

	function connError() {
		setCtx(true);
	};

	function wlanError() {
		setWlan(true);
	};

	//Display current Deck IP
	function displayIP(currIP: string) {
		setCurrIp(currIP);
	};

	//clean localStorage once connection has been estalished
	function clearStorage() {
		localStorage.removeItem("checkd");
		localStorage.removeItem("loading");
		localStorage.removeItem("storagep");
		localStorage.removeItem("ctx");
		localStorage.removeItem("wlan");
		localStorage.removeItem("thisIp");
	};

	function dynamicDesc(c:boolean, l:boolean):string {
		let desc = ""
		if (c == true && l == false) {
			desc = "Latency is being mitigated now. Toggling this off while ingame will disconnect you from the game. Make sure to toggle this off after you have finished playing!"
		}

		if (c == true && l == true) {
			desc = "Mitigation is being enabled"
		}

		if (c == false && l == false) {
			desc = "Enable this before starting FFXIV - this will create a container that will run XivMitmLatencyMitigator"
		}

		if (c == false && l == true) {
			desc = "Mitigation is now being disabled"
		}
		return desc
	};

	const onClick = async(e:boolean) => {
		call("toggle_status",{ checkd: e });
		setCheckd(e);
		setLoading(true);
	}
	useEffect(()=>{
		addEventListener('turnToggleOff',disableToggle);
		addEventListener('turnToggleOn',enableToggle);
		addEventListener('storageConfErrPrompt',storageConfError);
		addEventListener('connectionErrPrompt',connError);
		addEventListener('wlan0ConnError',wlanError);
		addEventListener('Vlan_IP',displayIP);
		addEventListener('clearStorage',clearStorage);
	return() => {
		removeEventListener('turnToggleOff',disableToggle);
		removeEventListener('turnToggleOn',enableToggle);
		removeEventListener('storageConfErrPrompt',storageConfError);
		removeEventListener('connectionErrPrompt',connError);
		removeEventListener('wlan0ConnError',wlanError);
		removeEventListener('Vlan_IP',displayIP);
		removeEventListener('clearStorage',clearStorage);
		}
	},[]);

	const initState = async () => {
		const getIsEnabledResponse = await call<[],boolean>("curr_status");
		setCheckd(getIsEnabledResponse);
		clearStorage();
	}
	useEffect(() => {
			initState();
	}, []);
	return (
		<PanelSection>
			<PanelSectionRow>
				<div style={{display:"flex", justifyContent: "center"}} >
					<img src={logo} />
				</div>
			</PanelSectionRow>
			<PanelSectionRow>
			<ToggleField
					label="Latency Mitigation"
					description={dynamicDesc(checkd,loading)}
					checked={checkd}
					disabled={loading}
					icon={<GiOmega/>}
					onChange={ async(e) => { onClick(e); }}
			/>
			</PanelSectionRow>
			{checkd && !loading && (<PanelSectionRow><div style={textStyle}>Steam Deck current IP: {thisIp} </div></PanelSectionRow>)}
			{checkd && loading && (<PanelSectionRow><div style={textStyle}>Please wait...<Spinner width="11" height="11"/></div></PanelSectionRow>)}
			{storagep && (<PanelSectionRow><div style={textStyle}><b>ERROR: storage.conf couldn't be created in /etc/containers. Please reload plugin from Decky Menu and try again.</b></div></PanelSectionRow>)}
			{ctx && (<PanelSectionRow><div style={textStyle}><b>ERROR: Connection to the game servers couldn't be established. Please reload plugin from Decky Menu and try again.</b></div></PanelSectionRow>)}
			{wlan && (<PanelSectionRow><div style={textStyle}><b>ERROR: Network Device couldn't be found. Please reload plugin from Decky Menu and try again.</b></div></PanelSectionRow>)}
			{!checkd && !loading && (<div></div>)}
			{!checkd && loading && (<PanelSectionRow><div style={textStyle}>Please wait...<Spinner width="11" height="11"/></div></PanelSectionRow>)}			
			<PanelSectionRow>
				<ButtonItem
          			layout="below"
					onClick={() => {
						Router.CloseSideMenus();
						Router.Navigate("/xivomega-settings")
					}}>
					<AiOutlineSetting/> Settings
				</ButtonItem>
				<ButtonItem
          			layout="below"
					onClick={() => {
						Navigation.Navigate("/xivomega-log");
					}}>
					<AiOutlineRightSquare/> View Log 
				</ButtonItem>
				<ButtonItem
          			layout="below"
					onClick={() => {
            		Navigation.NavigateToExternalWeb("https://github.com/shingonati0n/decky-plugin-xivomega");
					}}>
					<AiFillGithub/> GitHub HomePage
				</ButtonItem>
				<ButtonItem
					description="Any donation and support is greatly appreciated :D"
					layout="below"
					onClick={(e) => {
						showContextMenu(
							<Menu label="QR Code for ko-fi" cancelText="Go back" onCancel={() => {}}>
								<div style={{display:"flex", justifyContent: "center"}} >
									<img src={qrc} />
								</div>
								<MenuItem onSelected={() => {Navigation.NavigateToExternalWeb("https://ko-fi.com/ugo_shingonati0n");}}>Visit ko-fi Page</MenuItem>
							</Menu>,
							e.currentTarget ?? window
						)
					}}>
					<AiFillHeart/> Donate on ko-fi
				</ButtonItem>
			</PanelSectionRow>
		</PanelSection>
	);
};

export default definePlugin(() => {
	routerHook.addRoute("/xivomega-log",() =>(<LogRouter/>));
	routerHook.addRoute("/xivomega-opcode",() =>(<OpcodeRouter/>));
	routerHook.addRoute("/xivomega-settings",() =>(<SettingsRouter/>));
	return {
		name: "XivOmega",
		title: <div className={staticClasses.Title}>XivOmega</div>,
		content: <Content />,
		icon: <GiCagedBall />,
		onDismount() {
			onKill();
			xivOmegaSessionClear();
			localStorage.removeItem("useOpcode");
			localStorage.removeItem("c2s_ar");
			localStorage.removeItem("c2s_argt");
			localStorage.removeItem("s2c_ae01");
			localStorage.removeItem("s2c_ae08");
			localStorage.removeItem("s2c_ae16");
			localStorage.removeItem("s2c_ae24");
			localStorage.removeItem("s2c_ae32");
			localStorage.removeItem("s2c_ac");
			localStorage.removeItem("s2c_acntl");
			localStorage.removeItem("s2c_acntls");
			routerHook.removeRoute("/xivomega-log");
			routerHook.removeRoute("/xivomega-opcode");
			routerHook.removeRoute("/xivomega-settings");
		},
	};
});