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

const onKill = async() => {call('stop_status')}

function Content() {
	const [checkd, setCheckd] = useState<boolean>(false);

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
				Logo Goes Here
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
					<strong>
						<em>Mitigation Protocol ON</em>
					</strong>
					<br/>
					Latency is being mitigated now. If toggling this
					while playing, you will be disconnected from the game.
					<em>Make sure to toggle this off after you have finished playing!</em>
				</div>
			)}
			{!checkd && (
				<div>
					<strong>
						<em>Mitigation Protocol OFF</em>
					<br />
					Toggle this <em>before</em> starting your game. This will 
					enbale a container and will run the XivMitmLatencyMitigator as if 
					you were using it in another machine.
					</strong>
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
