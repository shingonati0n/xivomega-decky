import {
	PanelSection,
	PanelSectionRow,
	ToggleField,
	Spinner,
	staticClasses,
	ButtonItem,
	Navigation
} from "@decky/ui";

import {
	addEventListener,
	removeEventListener,
	call,
	definePlugin,
} from "@decky/api"

import { useState, useEffect } from "react";
import { BiTv, BiQr } from "react-icons/bi";
import { AiFillGithub, AiFillHeart } from "react-icons/ai";

import logo from "../assets/XIVOmegaLogo.png";

const onKill = async() => {call('stop_status')}

function Content() {
	const [checkd, setCheckd] = useState<boolean>(false);
	const [loading,setLoading] = useState<boolean>(false);
	const [storagep,setStoragep] = useState<boolean>(false);
	const [ctx,setCtx] = useState<boolean>(false);
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
	return() => {
		removeEventListener('turnToggleOff',disableToggle);
		removeEventListener('turnToggleOn',enableToggle);
		removeEventListener('storageConfErrPrompt',storageConfError);
		removeEventListener('connectionErrPrompt',connError);
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
					onChange={ async(e) => { onClick(e); }}
			/>
			</PanelSectionRow>
			{checkd && !loading && (<div></div>)}
			{checkd && loading && (<PanelSectionRow><div style={textStyle}>Please wait...<Spinner width="11" height="11"/></div></PanelSectionRow>)}
			{storagep && (<PanelSectionRow><div style={textStyle}><b>ERROR: storage.conf couldn't be created in /etc/containers. Please reload plugin from Decky Menu and try again.</b></div></PanelSectionRow>)}
			{ctx && (<PanelSectionRow><div style={textStyle}><b>ERROR: Connection to the game servers couldn't be established. Please reload plugin from Decky Menu and try again.</b></div></PanelSectionRow>)}
			{!checkd && !loading && (<div></div>)}
			{!checkd && loading && (<PanelSectionRow><div style={textStyle}>Please wait...<Spinner width="11" height="11"/></div></PanelSectionRow>)}			
			<PanelSectionRow>
				<ButtonItem
          			layout="below"
					onClick={() => {
            		Navigation.NavigateToExternalWeb("https://github.com/shingonati0n/decky-plugin-xivomega");
					}}>
					<AiFillGithub/> GitHub Page
				</ButtonItem>
				<ButtonItem 
          			layout="inline"
					bottomSeparator="none"
					onClick={() => {
            		Navigation.Navigate("../assets/qr_code.png");
					}}>
					<BiQr/>
				</ButtonItem>
				<ButtonItem
          			layout="inline"
					description="If this was useful, please consider donating :)"
					onClick={() => {
            		Navigation.NavigateToExternalWeb("https://ko-fi.com/ugo_shingonati0n");
					}}>
					<AiFillHeart/> Donate
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
		icon: <BiTv />,
		onDismount() {
			onKill();
		},
	};
});
