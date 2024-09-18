import {
	PanelSection,
	PanelSectionRow,
	ToggleField,
	staticClasses,
} from "@decky/ui";

import {
//	callable,
	call,
	definePlugin,
} from "@decky/api"

import { useState, useEffect } from "react";
import { BiTv } from "react-icons/bi";

import logo from "../assets/XIVOmegaLogo.png";

const onKill = async() => {call('stop_status')}

function Content() {
	const [checkd, setCheckd] = useState<boolean>(false);
	//const [loading,setLoading] = useState<boolean>(false);
	
	const onClick = async(e:boolean) => {
		call("toggle_status",{ checkd: e });
	};

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
					//ToDo: Disable toggling while podman elements are changing - special care on connecting and Retrying!
					onChange={ async(e) => { setCheckd(e); onClick(e); }}
			/>
			</PanelSectionRow>
			<PanelSectionRow>
			{checkd && (
				<div>
						Mitigation Protocol <b>ON</b>
					<br/>
					Latency is being mitigated now. <b>Toggling this off
					while ingame will disconnect you from the game.</b>
					<em><b>Make sure to toggle this off after you have finished playing!</b></em>
				</div>
			)}
			{!checkd && (
				<div>
						Mitigation Protocol <b>OFF</b>
					<br />
					Toggle this <b>before</b> starting your game. This will 
					enable a container and will run the XivMitmLatencyMitigator as if 
					you were using it in another machine.
				</div>
			)}
			</PanelSectionRow>
			<PanelSectionRow> 
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
