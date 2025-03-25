import { SidebarNavigation } from '@decky/ui';
import { OpcodeRouter } from './opcodes';
import { FC } from 'react';

export const SettingsRouter: FC = () => {
    return (
        <SidebarNavigation
            title="Settings"
            showTitle={true}
            pages={[
                {
                    title: "Opcode Configuration",
                    content: <OpcodeRouter />,
                    route: "/xivomega-opcode"
                }
            ]}
        />
    );
};