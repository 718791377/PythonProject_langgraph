import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1180
    height: 720
    minimumWidth: 960
    minimumHeight: 600
    visible: true
    title: "Project MOE Agent Console"

    readonly property var vm: JSON.parse(viewModelJson || "{}")
    readonly property var banner: vm.top_banner || ({})
    readonly property var statusCards: vm.status_cards || []
    readonly property var sessionRows: ((vm.session_table || {}).rows || [])
    readonly property var expertWorkbench: vm.expert_workbench || ({})
    readonly property var expertLenses: expertWorkbench.lenses || []
    readonly property var taskTemplates: expertWorkbench.task_templates || []
    readonly property var blockers: vm.banners || []
    property string selectedSection: "overview"
    property bool darkMode: true

    Material.theme: darkMode ? Material.Dark : Material.Light
    Material.accent: Material.Teal

    color: darkMode ? "#111827" : "#f6f8fb"

    function selectedLens() {
        if (expertLenses.length === 0)
            return ({ "label": "No expert lens", "description": "" })
        return expertLenses[Math.max(0, lensCombo.currentIndex)] || expertLenses[0]
    }

    function selectedTemplate() {
        if (taskTemplates.length === 0)
            return ({ "label": "Default task", "prompt": "" })
        return taskTemplates[Math.max(0, taskCombo.currentIndex)] || taskTemplates[0]
    }

    function generatedBriefText() {
        var lens = selectedLens()
        var task = selectedTemplate()
        var target = reviewTarget.text.length ? reviewTarget.text : "<paste target text, file path, or revision objective here>"
        return "Project MOE Expert Brief (draft only; no model execution)\n"
            + "Project: " + (banner.project_root || "Unknown project") + "\n"
            + "Agent: " + (banner.agent_name || "agent") + "\n"
            + "Namespace: " + (banner.state_namespace || "unknown") + "\n"
            + "Expert lens: " + (lens.label || lens.id || "lens") + "\n"
            + "Task template: " + (task.label || task.id || "template") + "\n\n"
            + "Review target / objective:\n" + target + "\n\n"
            + "Instructions:\n" + (task.prompt || "Assess with the selected expert lens and return actionable next steps.") + "\n\n"
            + "Execution boundary: generate brief only; do not start Codex, subagents, model APIs, or write project state."
    }

    component StatCard: Rectangle {
        id: statCard
        property string titleText: ""
        property string valueText: ""
        property string tokenText: ""
        Layout.fillWidth: true
        Layout.preferredHeight: 128
        radius: 18
        border.width: 1
        border.color: darkMode ? "#334155" : "#d9e2ec"
        color: darkMode ? "#1f2937" : "#ffffff"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 8
            Label {
                text: statCard.titleText
                color: darkMode ? "#9ca3af" : "#64748b"
                font.pixelSize: 13
                Layout.fillWidth: true
            }
            Label {
                text: statCard.valueText
                color: darkMode ? "#f8fafc" : "#0f172a"
                font.pixelSize: 24
                font.bold: true
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
            Rectangle {
                radius: 10
                color: statCard.tokenText === "ok" ? "#0f766e" : "#b45309"
                Layout.preferredHeight: 28
                Layout.preferredWidth: Math.max(72, tokenLabel.implicitWidth + 24)
                Label {
                    id: tokenLabel
                    anchors.centerIn: parent
                    text: statCard.tokenText || "unknown"
                    color: "white"
                    font.pixelSize: 12
                    font.bold: true
                }
            }
        }
    }

    component SideButton: Button {
        property string sectionId: ""
        Layout.fillWidth: true
        flat: true
        highlighted: root.selectedSection === sectionId
        onClicked: root.selectedSection = sectionId
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: 242
            color: darkMode ? "#0b1220" : "#ffffff"
            border.width: 1
            border.color: darkMode ? "#1e293b" : "#e2e8f0"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 14

                Label {
                    text: "Project MOE"
                    color: darkMode ? "#f8fafc" : "#0f172a"
                    font.pixelSize: 24
                    font.bold: true
                    Layout.fillWidth: true
                }
                Label {
                    text: banner.agent_name || "agent"
                    color: darkMode ? "#94a3b8" : "#64748b"
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                }
                Item { Layout.preferredHeight: 8 }
                SideButton { text: "Project"; sectionId: "overview" }
                SideButton { text: "Sessions"; sectionId: "sessions" }
                SideButton { text: "Expert Workbench"; sectionId: "workbench" }
                SideButton { text: "Diagnostics"; sectionId: "diagnostics" }
                SideButton { text: "Settings"; sectionId: "settings" }
                Item { Layout.fillHeight: true }
                Switch {
                    text: darkMode ? "Dark theme" : "Light theme"
                    checked: darkMode
                    onToggled: darkMode = checked
                    Layout.fillWidth: true
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 18
            Layout.margins: 22

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 92
                radius: 20
                color: darkMode ? "#172033" : "#ffffff"
                border.color: darkMode ? "#334155" : "#e2e8f0"
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 14
                    ColumnLayout {
                        Layout.fillWidth: true
                        Label {
                            text: banner.project_root || "Unknown project"
                            color: darkMode ? "#f8fafc" : "#0f172a"
                            font.pixelSize: 20
                            font.bold: true
                            elide: Text.ElideMiddle
                            Layout.fillWidth: true
                        }
                        Label {
                            text: "branch: " + (banner.current_branch || "unknown") + "    namespace: " + (banner.state_namespace || "unknown")
                            color: darkMode ? "#94a3b8" : "#64748b"
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                    }
                    Label {
                        text: ((vm.visual || {}).library || "Qt Quick/QML")
                        color: "#14b8a6"
                        font.bold: true
                    }
                }
            }

            GridLayout {
                visible: selectedSection === "overview"
                Layout.fillWidth: true
                columns: 4
                columnSpacing: 14
                rowSpacing: 14
                Repeater {
                    model: statusCards
                    StatCard {
                        titleText: modelData.title || ""
                        valueText: modelData.value || ""
                        tokenText: modelData.token || ""
                    }
                }
            }

            Rectangle {
                visible: selectedSection === "sessions"
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 20
                color: darkMode ? "#172033" : "#ffffff"
                border.color: darkMode ? "#334155" : "#e2e8f0"
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    Label {
                        text: "Sessions"
                        font.pixelSize: 22
                        font.bold: true
                        color: darkMode ? "#f8fafc" : "#0f172a"
                    }
                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: sessionRows
                        delegate: Rectangle {
                            width: ListView.view.width
                            height: 62
                            radius: 12
                            color: index % 2 === 0 ? (darkMode ? "#1f2937" : "#f8fafc") : "transparent"
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                Label { text: modelData.display_id || modelData.session_id || "session"; Layout.fillWidth: true; color: darkMode ? "#e5e7eb" : "#0f172a" }
                                Label { text: modelData.label || "unknown"; color: darkMode ? "#cbd5e1" : "#475569" }
                                Label { text: modelData.token || ""; color: (modelData.token || "") === "ok" ? "#14b8a6" : "#f59e0b" }
                            }
                        }
                    }
                }
            }

            Rectangle {
                visible: selectedSection === "workbench"
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 20
                color: darkMode ? "#172033" : "#ffffff"
                border.color: darkMode ? "#334155" : "#e2e8f0"
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12
                    Label {
                        text: expertWorkbench.title || "Expert Workbench"
                        font.pixelSize: 22
                        font.bold: true
                        color: darkMode ? "#f8fafc" : "#0f172a"
                    }
                    Label {
                        text: expertWorkbench.subtitle || "Generate a brief without executing a model."
                        wrapMode: Text.Wrap
                        color: darkMode ? "#cbd5e1" : "#475569"
                        Layout.fillWidth: true
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        ColumnLayout {
                            Layout.fillWidth: true
                            Label { text: "Expert lens"; color: darkMode ? "#94a3b8" : "#64748b" }
                            ComboBox {
                                id: lensCombo
                                Layout.fillWidth: true
                                model: expertLenses
                                textRole: "label"
                            }
                            Label {
                                text: (selectedLens().description || "")
                                wrapMode: Text.Wrap
                                color: darkMode ? "#cbd5e1" : "#475569"
                                Layout.fillWidth: true
                            }
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            Label { text: "Task template"; color: darkMode ? "#94a3b8" : "#64748b" }
                            ComboBox {
                                id: taskCombo
                                Layout.fillWidth: true
                                model: taskTemplates
                                textRole: "label"
                            }
                            Label {
                                text: (selectedTemplate().objective || "")
                                wrapMode: Text.Wrap
                                color: darkMode ? "#cbd5e1" : "#475569"
                                Layout.fillWidth: true
                            }
                        }
                    }
                    TextArea {
                        id: reviewTarget
                        Layout.fillWidth: true
                        Layout.preferredHeight: 96
                        placeholderText: "Paste target text, file path, or revision objective here. It stays in GUI runtime memory."
                        wrapMode: TextEdit.Wrap
                    }
                    TextArea {
                        id: briefPreview
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        readOnly: true
                        wrapMode: TextEdit.Wrap
                        text: generatedBriefText()
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Button {
                            text: "Copy brief"
                            onClicked: {
                                briefPreview.selectAll()
                                briefPreview.copy()
                                copyStatus.text = "Copied to clipboard; no disk or Git write."
                            }
                        }
                        Label {
                            id: copyStatus
                            Layout.fillWidth: true
                            text: "Brief persistence: runtime + clipboard only."
                            color: darkMode ? "#94a3b8" : "#64748b"
                        }
                    }
                }
            }

            Rectangle {
                visible: selectedSection === "diagnostics"
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 20
                color: darkMode ? "#172033" : "#ffffff"
                border.color: darkMode ? "#334155" : "#e2e8f0"
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    Label { text: "Diagnostics"; font.pixelSize: 22; font.bold: true; color: darkMode ? "#f8fafc" : "#0f172a" }
                    Repeater {
                        model: blockers.length ? blockers : [{"token": "ok", "message": "No blockers."}]
                        Label {
                            text: (modelData.token || "unknown") + " — " + (modelData.message || "")
                            wrapMode: Text.Wrap
                            color: (modelData.token || "") === "ok" ? "#14b8a6" : "#f59e0b"
                            Layout.fillWidth: true
                        }
                    }
                }
            }

            Rectangle {
                visible: selectedSection === "settings"
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 20
                color: darkMode ? "#172033" : "#ffffff"
                border.color: darkMode ? "#334155" : "#e2e8f0"
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    Label { text: "Settings"; font.pixelSize: 22; font.bold: true; color: darkMode ? "#f8fafc" : "#0f172a" }
                    Label { text: "Close behavior: ask before exit or hide to tray"; color: darkMode ? "#cbd5e1" : "#475569" }
                    Label { text: "Theme: Material / " + (darkMode ? "Dark" : "Light"); color: darkMode ? "#cbd5e1" : "#475569" }
                }
            }

            Label {
                Layout.fillWidth: true
                text: "F5 refresh · Alt+P project on · Alt+Shift+P project off · explicit tray hide only"
                color: darkMode ? "#94a3b8" : "#64748b"
                horizontalAlignment: Text.AlignRight
            }
        }
    }
}
