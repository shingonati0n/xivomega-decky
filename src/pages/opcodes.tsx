import { ToggleField, PanelSection, PanelSectionRow, TextField } from '@decky/ui';
import { FC, useEffect } from 'react';
import { VscCode } from 'react-icons/vsc'
import { call } from "@decky/api"
import { useLocalStorage } from "../useLocalStorage";

export const OpcodeRouter: FC = () => {
    const [useOpcode, setUseOpcode] = useLocalStorage("useOpcode",false);
    const [c2s_ar, setC2s_ar] = useLocalStorage("c2s_ar","0x0000");
    const [c2s_argt, setC2s_argt] = useLocalStorage("c2s_argt","0x0000");
    const [s2c_ae01, setS2c_ae01] = useLocalStorage("s2c_ae01","0x0000");
    const [s2c_ae08, setS2c_ae08] = useLocalStorage("s2c_ae08","0x0000");
    const [s2c_ae16, setS2c_ae16] = useLocalStorage("s2c_ae16","0x0000");
    const [s2c_ae24, setS2c_ae24] = useLocalStorage("s2c_ae24","0x0000");
    const [s2c_ae32, setS2c_ae32] = useLocalStorage("s2c_ae32","0x0000");
    const [s2c_ac, setS2c_ac] = useLocalStorage("s2c_ac","0x0000");
    const [s2c_acntl, setS2c_acntl] = useLocalStorage("s2c_acntl","0x0000");
    const [s2c_acntls, setS2c_acntls] = useLocalStorage("s2c_acntls","0x0000");
    
    const onClick = async(e:boolean) => {
        call("use_cust_opcodes",
            e, 
            c2s_ar,
            c2s_argt,
            s2c_ae01,
            s2c_ae08,
            s2c_ae16,
            s2c_ae24,
            s2c_ae32,
            s2c_ac,
            s2c_acntl,
            s2c_acntls);
            setUseOpcode(e);

    };
    useEffect(() => {
    },[]);
    return (
            <PanelSection>
                <PanelSectionRow>
                    <ToggleField
                            label="Use custom opcodes"
                            description={"Update the values below before enabling this. Make sure the correct values are input or else, mitigation won't work. Requires Latency Mitigation Restart to take effect."}
                            checked={useOpcode}
                            icon={<VscCode/>}
                            onChange={ async(e) => { onClick(e); }}
                    />
                </PanelSectionRow>
                <PanelSectionRow><TextField label="C2S_ActionRequest" defaultValue={c2s_ar} onChange={(e) => setC2s_ar(e.target.value)}/></PanelSectionRow>
                <PanelSectionRow><TextField label="C2S_ActionRequestGroundTargeted" defaultValue={c2s_argt} onChange={(e) => setC2s_argt(e.target.value)}/></PanelSectionRow>
                <PanelSectionRow><TextField label="S2C_ActionEffect01" defaultValue={s2c_ae01} onChange={(e) => setS2c_ae01(e.target.value)}/></PanelSectionRow>
                <PanelSectionRow><TextField label="S2C_ActionEffect08" defaultValue={s2c_ae08} onChange={(e) => setS2c_ae08(e.target.value)}/></PanelSectionRow>
                <PanelSectionRow><TextField label="S2C_ActionEffect16" defaultValue={s2c_ae16} onChange={(e) => setS2c_ae16(e.target.value)}/></PanelSectionRow>
                <PanelSectionRow><TextField label="S2C_ActionEffect24" defaultValue={s2c_ae24} onChange={(e) => setS2c_ae24(e.target.value)}/></PanelSectionRow>
                <PanelSectionRow><TextField label="S2C_ActionEffect32" defaultValue={s2c_ae32} onChange={(e) => setS2c_ae32(e.target.value)}/></PanelSectionRow>
                <PanelSectionRow><TextField label="S2C_ActorCast" defaultValue={s2c_ac} onChange={(e) => setS2c_ac(e.target.value)}/></PanelSectionRow>
                <PanelSectionRow><TextField label="S2C_ActorControl" defaultValue={s2c_acntl} onChange={(e) => setS2c_acntl(e.target.value)}/></PanelSectionRow>
                <PanelSectionRow><TextField label="S2C_ActorControlSelf" defaultValue={s2c_acntls} onChange={(e) => setS2c_acntls(e.target.value)}/></PanelSectionRow>
            </PanelSection>
    );
};