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
			<ToggleField
					label="Enable Mitigation"
					checked={checkd}
					onChange={ async(e) => { setCheckd(e); onClick(e); }}
			/>
			</PanelSectionRow>
			<PanelSectionRow>
			{checkd && (
				<div>
					<strong>
						<em>Mitigator Enabled</em>
					</strong>
				
				</div>
			)}
			{!checkd && (
				<div>
					<strong>
						<em>False False</em>
					</strong>
				
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
