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
	MenuItem
} from "@decky/ui";

import {
	addEventListener,
	removeEventListener,
	call,
	definePlugin,
} from "@decky/api"

import { useState, useEffect } from "react";
import { GiCagedBall,GiOmega } from 'react-icons/gi'
import { AiFillGithub, AiFillHeart } from "react-icons/ai";

import logo from "../assets/XIVOmegaLogo.png";
import qrc from "../assets/qr_code.png";

const onKill = async() => {call('stop_status')}

function Content() {
	const [checkd, setCheckd] = useState<boolean>(false);
	const [loading,setLoading] = useState<boolean>(false);
	const [storagep,setStoragep] = useState<boolean>(false);
	const [ctx,setCtx] = useState<boolean>(false);
	const [wlan,setWlan] = useState<boolean>(false);
	const textStyle = {fontSize: "11px"};


	function enableToggle() {
		setLoading(false);
	};

	function disableToggle() {
		setLoading(true);
	};

	function storageConfError() {
		setStoragep(true);
	}

	function connError() {
		setCtx(true);
	}

	function wlanError() {
		setWlan(true);
	}

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
	return() => {
		removeEventListener('turnToggleOff',disableToggle);
		removeEventListener('turnToggleOn',enableToggle);
		removeEventListener('storageConfErrPrompt',storageConfError);
		removeEventListener('connectionErrPrompt',connError);
		removeEventListener('wlan0ConnError',wlanError);
		}
	},[]);

	const initState = async () => {
		const getIsEnabledResponse = await call<[],boolean>("curr_status");
		setCheckd(getIsEnabledResponse);
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
			{checkd && !loading && (<div></div>)}
			{checkd && loading && (<PanelSectionRow><div style={textStyle}>Please wait...<Spinner width="11" height="11"/></div></PanelSectionRow>)}
			{storagep && (<PanelSectionRow><div style={textStyle}><b>ERROR: storage.conf couldn't be created in /etc/containers. Please reload plugin from Decky Menu and try again.</b></div></PanelSectionRow>)}
			{ctx && (<PanelSectionRow><div style={textStyle}><b>ERROR: Connection to the game servers couldn't be established. Please reload plugin from Decky Menu and try again.</b></div></PanelSectionRow>)}
			{wlan && (<PanelSectionRow><div style={textStyle}><b>ERROR: Wifi device wlan0 couldn't be found. Please reload plugin from Decky Menu and try again.</b></div></PanelSectionRow>)}
			{!checkd && !loading && (<div></div>)}
			{!checkd && loading && (<PanelSectionRow><div style={textStyle}>Please wait...<Spinner width="11" height="11"/></div></PanelSectionRow>)}			
			<PanelSectionRow>
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
	return {
		name: "XivOmega",
		title: <div className={staticClasses.Title}>XivOmega</div>,
		content: <Content />,
		icon: <GiCagedBall />,
		onDismount() {
			onKill();
		},
	};
});
