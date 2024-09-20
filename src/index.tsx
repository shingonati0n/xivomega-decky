import {
	PanelSection,
	PanelSectionRow,
	ToggleField,
	staticClasses,
} from "@decky/ui";

import {
	addEventListener,
	removeEventListener,
	call,
	definePlugin,
} from "@decky/api"

import { useState, useEffect } from "react";
import { BiTv } from "react-icons/bi";

import logo from "../assets/XIVOmegaLogo.png";

const onKill = async() => {call('stop_status')}

function Content() {
	const [checkd, setCheckd] = useState<boolean>(false);
	const [loading,setLoading] = useState<boolean>(false);

	function enableToggle() {
		setLoading(false);
	};

	function disableToggle() {
		setLoading(true);
	};

	const onClick = async(e:boolean) => {
		call("toggle_status",{ checkd: e });
		setLoading(true);
	}
	
	useEffect(()=>{
		addEventListener('turnToggleOff',disableToggle);
		addEventListener('turnToggleOn',enableToggle);
	return() => {
		removeEventListener('turnToggleOff',disableToggle);
		removeEventListener('turnToggleOn',enableToggle);
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
					label="Enable Mitigation"
					checked={checkd}
					disabled={loading}
					onChange={ async(e) => { setCheckd(e); onClick(e); }}
			/>
			</PanelSectionRow>
			<PanelSectionRow>
			{checkd && !loading && (
				<div>
						Mitigation Protocol <b>ON</b>
					<br/>
					Latency is being mitigated now. <b>Toggling this off
					while ingame will disconnect you from the game.</b>
					<em><b>Make sure to toggle this off after you have finished playing!</b></em>
				</div>
			)}
			{checkd && loading && (
				<div>
						<b>Enabling Mitigator...</b>
					<br/>
					Mitigation protocol is currently being activated, please wait until completed
				</div>
			)}
			{!checkd && !loading && (
				<div>
						Mitigation Protocol <b>OFF</b>
					<br />
					Toggle this <b>before</b> starting your game. This will 
					enable a container and will run the XivMitmLatencyMitigator as if 
					you were using it in another machine.
				</div>
			)}
			{!checkd && loading && (
				<div>
						<b>Disabling Mitigator...</b>
					<br />
					XIVOmega is being turned off now. Please wait
				</div>
			)}			
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
