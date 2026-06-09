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

    property var vm: JSON.parse(viewModelJson || "{}")
    readonly property var banner: vm.top_banner || ({})
    readonly property var statusCards: vm.status_cards || []
    readonly property var sessionRows: ((vm.session_table || {}).rows || [])
    property string sessionSearchText: ""
    property string sessionFilterModeId: "all"
    property string sessionSortKeyId: "last_seen"
    readonly property var displayedSessionRows: filterAndSortSessionRows()
    property int selectedSessionIndex: 0
    readonly property var selectedSession: displayedSessionRows.length ? displayedSessionRows[Math.min(Math.max(selectedSessionIndex, 0), displayedSessionRows.length - 1)] : ({})
    readonly property var sessionLensPanel: vm.session_lens_panel || ({})
    readonly property var lensCatalog: vm.lens_catalog || ({})
    readonly property var sessionLenses: sessionLensPanel.lenses || lensCatalog.lenses || []
    readonly property var sessionCategories: sessionLensPanel.categories || lensCatalog.categories || []
    readonly property var expertWorkbench: vm.expert_workbench || ({})
    readonly property var expertLenses: expertWorkbench.lenses || []
    readonly property var handoffTargets: expertWorkbench.handoff_targets || []
    readonly property var taskTemplates: expertWorkbench.task_templates || []
    readonly property var blockers: vm.banners || []
    readonly property var projectDefaultCard: vm.project_default_card || ({})
    readonly property var sessionControls: (vm.session_table || {}).controls || ({})
    readonly property var sessionFilterModes: sessionControls.filter_modes || []
    readonly property var sessionSortKeys: sessionControls.sort_keys || []
    readonly property var uiStates: vm.ui_states || ({})
    readonly property var projectsPanel: vm.multi_project_panel || ({})
    readonly property var projectsRows: projectsPanel.projects || []
    property string selectedSection: "overview"
    property bool darkMode: true
    property string lastActionToken: "ok"
    property string lastActionMessage: "Ready"
    property string selectedSessionLensIdsJson: "[]"
    property string selectedSessionCategoryIdsJson: "[]"
    property string selectedWorkbenchLensIdsJson: "[]"

    Material.theme: darkMode ? Material.Dark : Material.Light
    Material.accent: Material.Teal

    color: darkMode ? "#111827" : "#f6f8fb"

    function checkedIdsFromModel(model) {
        var values = []
        for (var i = 0; i < model.count; i++) {
            var row = model.get(i)
            if (row.checked)
                values.push(row.value || row.id)
        }
        return values
    }

    function syncSessionSelectionJson() {
        selectedSessionLensIdsJson = JSON.stringify(checkedIdsFromModel(sessionLensCheckModel))
        selectedSessionCategoryIdsJson = JSON.stringify(checkedIdsFromModel(sessionCategoryCheckModel))
    }

    function syncWorkbenchSelectionJson() {
        selectedWorkbenchLensIdsJson = JSON.stringify(checkedIdsFromModel(workbenchLensCheckModel))
    }

    function modelFromItems(items, selectedIds) {
        var selected = {}
        for (var i = 0; i < selectedIds.length; i++)
            selected[String(selectedIds[i])] = true
        var rows = []
        for (var j = 0; j < items.length; j++) {
            var item = items[j] || ({})
            var id = String(item.id || item.value || "")
            rows.push({
                "value": id,
                "label": String(item.label || id),
                "description": String(item.description || ""),
                "checked": selected[id] === true
            })
        }
        return rows
    }

    ListModel { id: sessionLensCheckModel }
    ListModel { id: sessionCategoryCheckModel }
    ListModel { id: workbenchLensCheckModel }

    function resetCheckModel(model, rows) {
        model.clear()
        for (var i = 0; i < rows.length; i++)
            model.append(rows[i])
    }

    function resetSessionSelectionModels() {
        resetCheckModel(sessionLensCheckModel, modelFromItems(sessionLenses, selectedSession.selected_lenses || []))
        resetCheckModel(sessionCategoryCheckModel, modelFromItems(sessionCategories, selectedSession.selected_categories || []))
        syncSessionSelectionJson()
    }

    function resetWorkbenchLensModel() {
        var defaults = []
        if (expertLenses.length > 0)
            defaults.push(expertLenses[0].id || expertLenses[0].value)
        resetCheckModel(workbenchLensCheckModel, modelFromItems(expertLenses, defaults))
        syncWorkbenchSelectionJson()
    }

    function selectedWorkbenchLenses() {
        var ids = checkedIdsFromModel(workbenchLensCheckModel)
        var selected = []
        for (var i = 0; i < expertLenses.length; i++) {
            var item = expertLenses[i] || ({})
            if (ids.indexOf(String(item.id || item.value || "")) >= 0)
                selected.push(item)
        }
        if (selected.length === 0 && expertLenses.length > 0)
            selected.push(expertLenses[0])
        return selected
    }

    function selectedLens() {
        var lenses = selectedWorkbenchLenses()
        if (lenses.length === 0)
            return ({ "label": "No expert lens", "description": "" })
        return lenses[0]
    }

    function selectedTemplate() {
        if (taskTemplates.length === 0)
            return ({ "label": "Default task", "prompt": "" })
        return taskTemplates[Math.max(0, taskCombo.currentIndex)] || taskTemplates[0]
    }

    function selectedHandoffTarget() {
        if (handoffTargets.length === 0)
            return ({ "id": "main-session", "label": "Main session", "description": "" })
        return handoffTargets[Math.max(0, handoffTargetCombo.currentIndex)] || handoffTargets[0]
    }

    function comboRowId(model, index, fallback) {
        var row = (model || [])[Math.max(0, index)] || ({})
        return String(row.id || fallback)
    }

    function rowMatchesSessionSearch(row) {
        var query = String(root.sessionSearchText || "").toLowerCase()
        if (!query.length)
            return true
        var haystack = [
            row.session_id || "",
            row.display_id || "",
            row.label || "",
            row.source || "",
            row.token || "",
            row.directory || "",
            row.branch || "",
            row.thread_source || "",
            row.conversation_title || "",
            row.conversation_preview || "",
            row.effective_lens_mode || "",
            row.lens_selection_summary || "",
            row.effective_state_explanation || "",
            row.override_conflict_hint || ""
        ].join(" ").toLowerCase()
        return haystack.indexOf(query) >= 0
    }

    function rowMatchesSessionFilter(row) {
        var mode = root.sessionFilterModeId || "all"
        var token = String(row.token || "ok")
        var valid = row.valid !== false && token === "ok"
        if (mode === "enabled")
            return valid && row.enabled === true
        if (mode === "disabled")
            return valid && row.enabled === false
        if (mode === "blocked-invalid")
            return !valid
        return true
    }

    function compareSessionRows(left, right) {
        var key = root.sessionSortKeyId || "last_seen"
        var a = ""
        var b = ""
        if (key === "display_id") {
            a = String(left.display_id || left.session_id || "").toLowerCase()
            b = String(right.display_id || right.session_id || "").toLowerCase()
        } else if (key === "label") {
            a = String(left.label || "").toLowerCase()
            b = String(right.label || "").toLowerCase()
        } else if (key === "effective_lens_mode") {
            a = String(left.effective_lens_mode || "").toLowerCase()
            b = String(right.effective_lens_mode || "").toLowerCase()
        } else {
            a = String(right.last_seen_at || "")
            b = String(left.last_seen_at || "")
        }
        if (a < b)
            return -1
        if (a > b)
            return 1
        return 0
    }

    function filterAndSortSessionRows() {
        var rows = []
        for (var i = 0; i < sessionRows.length; i++) {
            var row = sessionRows[i] || ({})
            if (rowMatchesSessionSearch(row) && rowMatchesSessionFilter(row))
                rows.push(row)
        }
        rows.sort(compareSessionRows)
        return rows
    }

    function generatedHandoffPackageText() {
        var lenses = selectedWorkbenchLenses()
        var task = selectedTemplate()
        var handoffTarget = selectedHandoffTarget()
        var target = reviewTarget.text.length ? reviewTarget.text : "<paste target text, file path, or revision objective here>"
        var lensLines = ""
        for (var i = 0; i < lenses.length; i++) {
            var lens = lenses[i] || ({})
            lensLines += "- " + (lens.id || lens.label || "lens") + ": " + (lens.label || lens.id || "lens") + "\n"
        }
        return "Project MOE Expert Workbench v2 Handoff Package (draft only; no model execution)\n"
            + "Project: " + (banner.project_root || "Unknown project") + "\n"
            + "Agent: " + (banner.agent_name || "agent") + "\n"
            + "Namespace: " + (banner.state_namespace || "unknown") + "\n"
            + "Handoff target: " + (handoffTarget.id || "main-session") + " (" + (handoffTarget.label || "Main session") + ")\n"
            + "Selected MOE lenses:\n" + lensLines
            + "Task template: " + (task.label || task.id || "template") + "\n\n"
            + "Review target / objective:\n" + target + "\n\n"
            + "Instructions:\n" + (task.prompt || "Assess with the selected expert lens and return actionable next steps.") + "\n\n"
            + "Carrier instructions: main session may use selected MOE lenses directly, paste this package to a subagent, or hand it to a durable-team / langgraph-workflow.\n"
            + "Execution boundary: generate handoff package only; do not start Codex, subagents, durable teams, LangGraph workflows, model APIs, or write project state."
    }

    function updateFromBridgeResult(raw) {
        var payload = ({})
        try {
            payload = JSON.parse(raw || "{}")
        } catch (error) {
            lastActionToken = "blocked:invalid_bridge_json"
            lastActionMessage = String(error)
            return
        }
        lastActionToken = payload.token || "unknown"
        lastActionMessage = payload.message || ""
        if (payload.view_model) {
            vm = payload.view_model
            selectedSessionIndex = Math.min(Math.max(selectedSessionIndex, 0), Math.max(0, displayedSessionRows.length - 1))
            resetSessionSelectionModels()
            resetWorkbenchLensModel()
        }
    }

    function updateFromWorkbenchArtifactResult(raw, copyExport) {
        var payload = ({})
        try {
            payload = JSON.parse(raw || "{}")
        } catch (error) {
            copyStatus.text = "Workbench artifact action failed: invalid JSON"
            lastActionToken = "blocked:invalid_workbench_artifact_json"
            lastActionMessage = String(error)
            return
        }
        lastActionToken = payload.token || "unknown"
        lastActionMessage = payload.message || ""
        if (payload.export_text) {
            handoffPreview.text = payload.export_text
        }
        if (copyExport && payload.export_text) {
            handoffPreview.selectAll()
            handoffPreview.copy()
        }
        copyStatus.text = (payload.message || "Workbench artifact action completed.") + " token=" + lastActionToken
    }

    function executeProjectAction(action) {
        updateFromBridgeResult(projectMoeBridge.executeWriteAction(action, "", "[]", "[]"))
    }

    function executeSessionAction(action, lensesJson, categoriesJson) {
        if (!selectedSession.session_id) {
            lastActionToken = "blocked:missing_session_id"
            lastActionMessage = "Select a valid session first."
            return
        }
        updateFromBridgeResult(projectMoeBridge.executeWriteAction(action, selectedSession.session_id, lensesJson || "[]", categoriesJson || "[]"))
    }

    Component.onCompleted: {
        resetSessionSelectionModels()
        resetWorkbenchLensModel()
    }

    onSelectedSessionIndexChanged: resetSessionSelectionModels()
    onSessionSearchTextChanged: selectedSessionIndex = 0
    onSessionFilterModeIdChanged: selectedSessionIndex = 0
    onSessionSortKeyIdChanged: selectedSessionIndex = 0

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

    component SectionCard: Rectangle {
        Layout.fillWidth: true
        Layout.fillHeight: true
        radius: 20
        color: darkMode ? "#172033" : "#ffffff"
        border.color: darkMode ? "#334155" : "#e2e8f0"
        border.width: 1
        clip: true
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
                SideButton { text: "Projects"; sectionId: "projects" }
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
                visible: selectedSection === "overview"
                Layout.fillWidth: true
                Layout.preferredHeight: 86
                radius: 18
                border.width: 1
                border.color: darkMode ? "#334155" : "#e2e8f0"
                color: darkMode ? "#172033" : "#ffffff"
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 10
                    Button {
                        text: "Refresh"
                        onClicked: updateFromBridgeResult(projectMoeBridge.refreshViewModel())
                    }
                    Button {
                        text: "Enable project default"
                        onClicked: executeProjectAction("project-on")
                    }
                    Button {
                        text: "Disable project default"
                        onClicked: executeProjectAction("project-off")
                    }
                    Label {
                        Layout.fillWidth: true
                        text: "Project default: " + (projectDefaultCard.label || "unknown") + " / effective: " + (projectDefaultCard.effective_label || "unknown") + " / last action: " + lastActionToken
                        color: darkMode ? "#94a3b8" : "#64748b"
                        elide: Text.ElideRight
                    }
                }
            }

            SectionCard {
                visible: selectedSection === "sessions"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    Label {
                        text: "Sessions"
                        font.pixelSize: 22
                        font.bold: true
                        color: darkMode ? "#f8fafc" : "#0f172a"
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        TextField {
                            id: sessionSearch
                            Layout.fillWidth: true
                            placeholderText: "Search sessions"
                            text: root.sessionSearchText
                            onTextChanged: root.sessionSearchText = text
                        }
                        Label { text: "Filter"; color: darkMode ? "#94a3b8" : "#64748b" }
                        ComboBox {
                            id: sessionFilterCombo
                            Layout.preferredWidth: 150
                            model: sessionFilterModes.length ? sessionFilterModes : [{"id": "all", "label": "All"}]
                            textRole: "label"
                            onCurrentIndexChanged: root.sessionFilterModeId = comboRowId(model, currentIndex, "all")
                        }
                        Label { text: "Sort"; color: darkMode ? "#94a3b8" : "#64748b" }
                        ComboBox {
                            id: sessionSortCombo
                            Layout.preferredWidth: 170
                            model: sessionSortKeys.length ? sessionSortKeys : [{"id": "last_seen", "label": "Last seen"}]
                            textRole: "label"
                            onCurrentIndexChanged: root.sessionSortKeyId = comboRowId(model, currentIndex, "last_seen")
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 12

                        Rectangle {
                            Layout.preferredWidth: Math.min(340, Math.max(260, parent.width * 0.34))
                            Layout.fillHeight: true
                            radius: 16
                            border.width: 1
                            border.color: darkMode ? "#334155" : "#e2e8f0"
                            color: darkMode ? "#0f172a" : "#f8fafc"
                            clip: true

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 8
                                Label {
                                    text: "Session list"
                                    color: darkMode ? "#94a3b8" : "#64748b"
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }
                                ListView {
                                    id: sessionsList
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    boundsBehavior: Flickable.StopAtBounds
                                    model: displayedSessionRows
                                    delegate: Rectangle {
                                        width: ListView.view.width
                                        height: 210
                                        radius: 12
                                        color: index === root.selectedSessionIndex ? (darkMode ? "#0f766e" : "#ccfbf1") : (index % 2 === 0 ? (darkMode ? "#1f2937" : "#f8fafc") : "transparent")
                                        clip: true
                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: root.selectedSessionIndex = index
                                        }
                                        ColumnLayout {
                                            anchors.fill: parent
                                            anchors.margins: 8
                                            spacing: 2
                                            Label {
                                                text: (modelData.updated_relative || modelData.updated_at || modelData.last_seen_at || "") + "     " + (modelData.conversation_title || modelData.display_id || modelData.session_id || "session")
                                                Layout.fillWidth: true
                                                color: darkMode ? "#e5e7eb" : "#0f172a"
                                                elide: Text.ElideRight
                                            }
                                            Label {
                                                text: "| Session:    " + (modelData.visible_session_id || modelData.session_id || "")
                                                Layout.fillWidth: true
                                                color: darkMode ? "#cbd5e1" : "#475569"
                                                elide: Text.ElideMiddle
                                            }
                                            Label {
                                                text: "| Created:    " + (modelData.created_relative || "") + " - " + (modelData.created_display || modelData.created_at || "")
                                                Layout.fillWidth: true
                                                color: darkMode ? "#cbd5e1" : "#475569"
                                                elide: Text.ElideRight
                                            }
                                            Label {
                                                text: "| Updated:    " + (modelData.updated_relative || "") + " - " + (modelData.updated_display || modelData.updated_at || modelData.last_seen_at || "")
                                                Layout.fillWidth: true
                                                color: darkMode ? "#cbd5e1" : "#475569"
                                                elide: Text.ElideRight
                                            }
                                            Label {
                                                text: "| Directory:  " + (modelData.directory || "")
                                                Layout.fillWidth: true
                                                color: darkMode ? "#cbd5e1" : "#475569"
                                                elide: Text.ElideMiddle
                                            }
                                            Label {
                                                text: "| Branch:     " + (modelData.branch || "unknown") + "    | State: " + (modelData.label || "unknown") + "    | Lenses: " + (modelData.lens_selection_summary || "All lenses")
                                                Layout.fillWidth: true
                                                color: darkMode ? "#cbd5e1" : "#475569"
                                                elide: Text.ElideRight
                                            }
                                            Label {
                                                text: "| Conversation:"
                                                Layout.fillWidth: true
                                                color: darkMode ? "#cbd5e1" : "#475569"
                                            }
                                            Label {
                                                text: "| " + (modelData.conversation_preview || "(no preview)")
                                                Layout.fillWidth: true
                                                Layout.fillHeight: true
                                                color: darkMode ? "#e2e8f0" : "#334155"
                                                wrapMode: Text.WordWrap
                                                maximumLineCount: 4
                                                elide: Text.ElideRight
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 16
                            border.width: 1
                            border.color: darkMode ? "#334155" : "#e2e8f0"
                            color: darkMode ? "#0f172a" : "#f8fafc"
                            clip: true

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 8
                                Label {
                                    text: "Session MOE lenses"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: darkMode ? "#f8fafc" : "#0f172a"
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }
                                Label {
                                    text: "Selected session: " + (selectedSession.display_id || selectedSession.session_id || "(none)") + " - current: " + (selectedSession.lens_selection_summary || "All lenses")
                                    wrapMode: Text.Wrap
                                    color: darkMode ? "#cbd5e1" : "#475569"
                                    Layout.fillWidth: true
                                    Layout.maximumHeight: 44
                                    elide: Text.ElideRight
                                }
                                Label {
                                    text: "Empty selection = all lenses"
                                    color: "#14b8a6"
                                    font.bold: true
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }
                                Label {
                                    text: "Effective state: " + (selectedSession.effective_state_explanation || "No session selected")
                                    color: darkMode ? "#cbd5e1" : "#475569"
                                    wrapMode: Text.Wrap
                                    Layout.fillWidth: true
                                    Layout.maximumHeight: 42
                                    elide: Text.ElideRight
                                }
                                Label {
                                    text: "Override hint: " + (selectedSession.override_conflict_hint || "No session override")
                                    color: darkMode ? "#cbd5e1" : "#475569"
                                    wrapMode: Text.Wrap
                                    Layout.fillWidth: true
                                    Layout.maximumHeight: 42
                                    elide: Text.ElideRight
                                }
                                RowLayout {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    spacing: 12
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        Label { text: "Lenses"; color: darkMode ? "#94a3b8" : "#64748b"; Layout.fillWidth: true; elide: Text.ElideRight }
                                        ScrollView {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            clip: true
                                            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                                            ScrollBar.vertical.policy: ScrollBar.AsNeeded
                                            ColumnLayout {
                                                width: parent.availableWidth
                                                Repeater {
                                                    model: sessionLensCheckModel
                                                    CheckBox {
                                                        Layout.fillWidth: true
                                                        text: model.label
                                                        checked: model.checked
                                                        clip: true
                                                        onToggled: {
                                                            sessionLensCheckModel.setProperty(index, "checked", checked)
                                                            syncSessionSelectionJson()
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        Label { text: "Categories"; color: darkMode ? "#94a3b8" : "#64748b"; Layout.fillWidth: true; elide: Text.ElideRight }
                                        ScrollView {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            clip: true
                                            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                                            ScrollBar.vertical.policy: ScrollBar.AsNeeded
                                            ColumnLayout {
                                                width: parent.availableWidth
                                                Repeater {
                                                    model: sessionCategoryCheckModel
                                                    CheckBox {
                                                        Layout.fillWidth: true
                                                        text: model.label
                                                        checked: model.checked
                                                        clip: true
                                                        onToggled: {
                                                            sessionCategoryCheckModel.setProperty(index, "checked", checked)
                                                            syncSessionSelectionJson()
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                                GridLayout {
                                    Layout.fillWidth: true
                                    columns: 2
                                    columnSpacing: 8
                                    rowSpacing: 8
                                    Button {
                                        text: "Enable session MOE"
                                        Layout.fillWidth: true
                                        enabled: sessionRows.length > 0
                                        onClicked: executeSessionAction("session-on", selectedSessionLensIdsJson, selectedSessionCategoryIdsJson)
                                    }
                                    Button {
                                        text: "Disable session MOE"
                                        Layout.fillWidth: true
                                        enabled: sessionRows.length > 0
                                        onClicked: executeSessionAction("session-off", "[]", "[]")
                                    }
                                    Button {
                                        text: "Apply session lenses"
                                        Layout.fillWidth: true
                                        enabled: sessionRows.length > 0
                                        onClicked: executeSessionAction("session-set-lenses", selectedSessionLensIdsJson, selectedSessionCategoryIdsJson)
                                    }
                                    Button {
                                        text: "Clear session lenses"
                                        Layout.fillWidth: true
                                        enabled: sessionRows.length > 0
                                        onClicked: executeSessionAction("session-clear-lenses", "[]", "[]")
                                    }
                                }
                                Label {
                                    Layout.fillWidth: true
                                    text: lastActionToken + " - " + lastActionMessage
                                    color: darkMode ? "#94a3b8" : "#64748b"
                                    elide: Text.ElideRight
                                }
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
                        Layout.preferredHeight: 198
                        Layout.maximumHeight: 210
                        spacing: 12
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 14
                            clip: true
                            color: darkMode ? "#0f172a" : "#f8fafc"
                            border.color: darkMode ? "#334155" : "#e2e8f0"
                            border.width: 1
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 6
                                Label { text: "Expert lenses"; color: darkMode ? "#94a3b8" : "#64748b"; Layout.fillWidth: true; elide: Text.ElideRight }
                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                                    ScrollBar.vertical.policy: ScrollBar.AsNeeded
                                    ColumnLayout {
                                        width: parent.availableWidth
                                        Repeater {
                                            model: workbenchLensCheckModel
                                            CheckBox {
                                                Layout.fillWidth: true
                                                text: model.label
                                                checked: model.checked
                                                clip: true
                                                onToggled: {
                                                    workbenchLensCheckModel.setProperty(index, "checked", checked)
                                                    syncWorkbenchSelectionJson()
                                                }
                                            }
                                        }
                                    }
                                }
                                Label {
                                    text: "Select one or more MOE lenses; brief only."
                                    wrapMode: Text.Wrap
                                    color: darkMode ? "#cbd5e1" : "#475569"
                                    Layout.fillWidth: true
                                    Layout.maximumHeight: 36
                                    elide: Text.ElideRight
                                }
                            }
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 14
                            clip: true
                            color: darkMode ? "#0f172a" : "#f8fafc"
                            border.color: darkMode ? "#334155" : "#e2e8f0"
                            border.width: 1
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 8
                                Label { text: "Task template"; color: darkMode ? "#94a3b8" : "#64748b"; Layout.fillWidth: true; elide: Text.ElideRight }
                                ComboBox {
                                    id: taskCombo
                                    Layout.fillWidth: true
                                    model: taskTemplates
                                    textRole: "label"
                                }
                                Label {
                                    text: (selectedTemplate().objective || "")
                                    wrapMode: Text.NoWrap
                                    color: darkMode ? "#cbd5e1" : "#475569"
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 18
                                    Layout.maximumHeight: 20
                                    elide: Text.ElideRight
                                }
                            }
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 14
                            clip: true
                            color: darkMode ? "#0f172a" : "#f8fafc"
                            border.color: darkMode ? "#334155" : "#e2e8f0"
                            border.width: 1
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 8
                                Label { text: "Handoff target"; color: darkMode ? "#94a3b8" : "#64748b"; Layout.fillWidth: true; elide: Text.ElideRight }
                                ComboBox {
                                    id: handoffTargetCombo
                                    Layout.fillWidth: true
                                    model: handoffTargets
                                    textRole: "label"
                                }
                                Label {
                                    text: "main-session / subagent / durable-team / langgraph-workflow"
                                    wrapMode: Text.NoWrap
                                    color: darkMode ? "#cbd5e1" : "#475569"
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 18
                                    Layout.maximumHeight: 20
                                    elide: Text.ElideRight
                                }
                            }
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 12
                        TextArea {
                            id: reviewTarget
                            Layout.preferredWidth: 300
                            Layout.minimumWidth: 260
                            Layout.fillHeight: true
                            placeholderText: "Paste target text, file path, or revision objective here. It stays in GUI runtime memory."
                            wrapMode: TextEdit.Wrap
                        }
                        TextArea {
                            id: handoffPreview
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            readOnly: true
                            wrapMode: TextEdit.Wrap
                            text: generatedHandoffPackageText()
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 52
                        Button {
                            text: "Copy handoff package"
                            Layout.preferredWidth: 190
                            onClicked: {
                                handoffPreview.selectAll()
                                handoffPreview.copy()
                                copyStatus.text = "Copied to clipboard; no disk or Git write."
                            }
                        }
                        Button {
                            text: "Save draft"
                            Layout.preferredWidth: 128
                            onClicked: updateFromWorkbenchArtifactResult(
                                projectMoeBridge.saveHandoffDraft(
                                    selectedSession.session_id || "",
                                    selectedSession.display_id || "",
                                    selectedWorkbenchLensIdsJson,
                                    "[]",
                                    selectedHandoffTarget().id || "main-session",
                                    selectedTemplate().id || "default",
                                    reviewTarget.text
                                ),
                                false
                            )
                        }
                        Button {
                            text: "Export handoff package"
                            Layout.preferredWidth: 190
                            onClicked: updateFromWorkbenchArtifactResult(
                                projectMoeBridge.exportHandoffPackage(
                                    selectedSession.session_id || "",
                                    selectedSession.display_id || "",
                                    selectedWorkbenchLensIdsJson,
                                    "[]",
                                    selectedHandoffTarget().id || "main-session",
                                    selectedTemplate().id || "default",
                                    reviewTarget.text
                                ),
                                true
                            )
                        }
                        Label {
                            id: copyStatus
                            Layout.fillWidth: true
                            text: "Expert result history: drafts, copied exports, and queued packages stay in target runtime artifacts."
                            color: darkMode ? "#94a3b8" : "#64748b"
                            elide: Text.ElideRight
                        }
                    }
                }
            }

            Rectangle {
                visible: selectedSection === "projects"
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
                    Label { text: "Projects"; font.pixelSize: 22; font.bold: true; color: darkMode ? "#f8fafc" : "#0f172a" }
                    Label { text: "Install status"; color: darkMode ? "#94a3b8" : "#64748b"; Layout.fillWidth: true }
                    Label { text: "Dry-run update"; color: darkMode ? "#14b8a6" : "#0f766e"; Layout.fillWidth: true }
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        ColumnLayout {
                            width: parent.availableWidth
                            Repeater {
                                model: projectsRows.length ? projectsRows : [{"project_root": "No explicit managed project registry", "install_status": "empty", "installed_version": "none", "readiness_status": "unknown"}]
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 78
                                    radius: 14
                                    color: darkMode ? "#0f172a" : "#f8fafc"
                                    border.color: darkMode ? "#334155" : "#e2e8f0"
                                    border.width: 1
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        Label { text: modelData.project_root || "project"; Layout.fillWidth: true; elide: Text.ElideMiddle; color: darkMode ? "#e5e7eb" : "#0f172a" }
                                        Label { text: "Install status: " + (modelData.install_status || "unknown") + " / version: " + (modelData.installed_version || "none"); Layout.fillWidth: true; elide: Text.ElideRight; color: darkMode ? "#cbd5e1" : "#475569" }
                                        Label { text: "Dry-run update only; rollback hint is required before apply."; Layout.fillWidth: true; elide: Text.ElideRight; color: darkMode ? "#94a3b8" : "#64748b" }
                                    }
                                }
                            }
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
                            text: (modelData.token || "unknown") + " - " + (modelData.message || "")
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
                    Label { text: "Loading state: " + (((uiStates.loading || {}).message) || "No loading-state message"); color: darkMode ? "#cbd5e1" : "#475569"; wrapMode: Text.Wrap; Layout.fillWidth: true }
                    Label { text: "Empty state: " + (((uiStates.empty || {}).message) || "No empty-state message"); color: darkMode ? "#cbd5e1" : "#475569"; wrapMode: Text.Wrap; Layout.fillWidth: true }
                    Label { text: "Error state: " + (((uiStates.error || {}).message) || "No error-state message"); color: darkMode ? "#cbd5e1" : "#475569"; wrapMode: Text.Wrap; Layout.fillWidth: true }
                    Label { text: "Help: " + (((uiStates.help || {}).message) || "Use governed Project MOE controls only"); color: darkMode ? "#cbd5e1" : "#475569"; wrapMode: Text.Wrap; Layout.fillWidth: true }
                }
            }

            Label {
                Layout.fillWidth: true
                text: "F5 refresh - Alt+P project on - Alt+Shift+P project off - explicit tray hide only"
                color: darkMode ? "#94a3b8" : "#64748b"
                horizontalAlignment: Text.AlignRight
            }
        }
    }
}
