import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Discover tab - Model search and browsing
Item {
    id: root

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Search and filters section
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            color: "white"
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15

                // Search bar
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    TextField {
                        id: searchField
                        Layout.fillWidth: true
                        placeholderText: "Search models (e.g., 'Llama', 'Mistral', 'GGUF')..."
                        font.pixelSize: 14
                        
                        Keys.onReturnPressed: {
                            searchButton.clicked()
                        }
                    }

                    Button {
                        id: searchButton
                        text: "Search"
                        highlighted: true
                        onClicked: {
                            // TODO: Trigger search
                            console.log("Searching for:", searchField.text)
                        }
                    }
                }

                // Filters row
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 15

                    CheckBox {
                        id: ggufOnlyCheckbox
                        text: "GGUF files only"
                        checked: true
                    }

                    Label {
                        text: "Sort by:"
                        color: "#7f8c8d"
                    }

                    ComboBox {
                        id: sortComboBox
                        model: ["Downloads", "Likes", "Recently updated", "Recently created"]
                        currentIndex: 0
                    }

                    Item { Layout.fillWidth: true }

                    Label {
                        text: "0 results"
                        color: "#95a5a6"
                        font.pixelSize: 12
                    }
                }
            }
        }

        // Results area
        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal

            // Model list
            Rectangle {
                SplitView.preferredWidth: 400
                SplitView.minimumWidth: 300
                color: "#ecf0f1"

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    // List header
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        color: "#bdc3c7"

                        Label {
                            anchors.centerIn: parent
                            text: "Models"
                            font.bold: true
                        }
                    }

                    // Model list
                    ListView {
                        id: modelListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        
                        model: ListModel {
                            // Placeholder data
                            ListElement {
                                modelName: "Example Model"
                                modelAuthor: "TheBloke"
                                downloads: "1.2M"
                                ggufCount: "8"
                            }
                        }

                        delegate: ItemDelegate {
                            width: modelListView.width
                            height: 80

                            background: Rectangle {
                                color: modelListView.currentIndex === index ? "#3498db" : "white"
                                border.color: "#bdc3c7"
                                border.width: 1
                            }

                            contentItem: ColumnLayout {
                                spacing: 5
                                anchors.margins: 10

                                Label {
                                    text: modelName
                                    font.pixelSize: 14
                                    font.bold: true
                                    color: modelListView.currentIndex === index ? "white" : "#2c3e50"
                                }

                                Label {
                                    text: modelAuthor
                                    font.pixelSize: 12
                                    color: modelListView.currentIndex === index ? "#ecf0f1" : "#7f8c8d"
                                }

                                RowLayout {
                                    spacing: 15

                                    Label {
                                        text: "⬇️ " + downloads
                                        font.pixelSize: 11
                                        color: modelListView.currentIndex === index ? "#ecf0f1" : "#95a5a6"
                                    }

                                    Label {
                                        text: "📦 " + ggufCount + " GGUF"
                                        font.pixelSize: 11
                                        color: modelListView.currentIndex === index ? "#ecf0f1" : "#95a5a6"
                                    }
                                }
                            }

                            onClicked: {
                                modelListView.currentIndex = index
                            }
                        }

                        ScrollBar.vertical: ScrollBar {}
                    }

                    // Pagination
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 50
                        color: "#bdc3c7"

                        RowLayout {
                            anchors.centerIn: parent
                            spacing: 10

                            Button {
                                text: "◀ Previous"
                                enabled: false
                            }

                            Label {
                                text: "Page 1 of 1"
                                font.pixelSize: 12
                            }

                            Button {
                                text: "Next ▶"
                                enabled: false
                            }
                        }
                    }
                }
            }

            // Model details panel
            Rectangle {
                SplitView.fillWidth: true
                color: "white"

                ScrollView {
                    anchors.fill: parent
                    contentWidth: availableWidth

                    ColumnLayout {
                        width: parent.width
                        spacing: 20
                        anchors.margins: 20

                        // Header
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 5

                            Label {
                                text: "Select a model"
                                font.pixelSize: 24
                                font.bold: true
                            }

                            Label {
                                text: "Model details will appear here"
                                font.pixelSize: 14
                                color: "#7f8c8d"
                            }
                        }

                        // Placeholder content
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 200
                            color: "#ecf0f1"
                            radius: 5

                            Label {
                                anchors.centerIn: parent
                                text: "No model selected"
                                color: "#95a5a6"
                                font.pixelSize: 16
                            }
                        }

                        Item { Layout.fillHeight: true }
                    }
                }
            }
        }
    }
}
