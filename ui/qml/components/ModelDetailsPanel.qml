import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Model details panel with file list
ScrollView {
    id: root
    contentWidth: availableWidth

    property var modelData: null

    ColumnLayout {
        width: root.width
        spacing: 20
        anchors.margins: 20

        // Model header
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 10

            Label {
                text: modelData ? modelData.name : "No model selected"
                font.pixelSize: 24
                font.bold: true
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            Label {
                text: modelData ? "by " + modelData.author : ""
                font.pixelSize: 14
                color: "#7f8c8d"
                visible: modelData !== null
            }

            // Stats row
            RowLayout {
                spacing: 20
                visible: modelData !== null

                Label {
                    text: "⬇️ " + (modelData ? modelData.downloads : "0")
                    font.pixelSize: 12
                    color: "#95a5a6"
                }

                Label {
                    text: "❤️ " + (modelData ? modelData.likes : "0")
                    font.pixelSize: 12
                    color: "#95a5a6"
                }

                Label {
                    text: "💾 " + (modelData ? modelData.totalSize : "0 GB")
                    font.pixelSize: 12
                    color: "#95a5a6"
                }
            }
        }

        // Description
        GroupBox {
            Layout.fillWidth: true
            title: "Description"
            visible: modelData !== null && modelData.description

            Label {
                width: parent.width
                text: modelData ? modelData.description : ""
                wrapMode: Text.WordWrap
                font.pixelSize: 13
            }
        }

        // Tags
        GroupBox {
            Layout.fillWidth: true
            title: "Tags"
            visible: modelData !== null && modelData.tags && modelData.tags.length > 0

            Flow {
                width: parent.width
                spacing: 5

                Repeater {
                    model: modelData ? modelData.tags : []
                    
                    Rectangle {
                        height: 25
                        width: tagLabel.width + 16
                        color: "#3498db"
                        radius: 3

                        Label {
                            id: tagLabel
                            anchors.centerIn: parent
                            text: modelData.tags[index]
                            color: "white"
                            font.pixelSize: 11
                        }
                    }
                }
            }
        }

        // Files list (GGUF prioritised)
        GroupBox {
            Layout.fillWidth: true
            title: "Files " + (modelData ? "(" + modelData.fileCount + ")" : "")
            visible: modelData !== null

            ColumnLayout {
                width: parent.width
                spacing: 10

                // Filter for GGUF only
                CheckBox {
                    id: ggufOnlyFilter
                    text: "Show GGUF files only"
                    checked: true
                }

                // File list
                ListView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.min(contentHeight, 400)
                    clip: true
                    
                    model: ListModel {
                        id: filesModel
                        // Will be populated from modelData
                    }

                    delegate: ItemDelegate {
                        width: parent.width
                        height: 60

                        background: Rectangle {
                            color: index % 2 === 0 ? "#f8f9fa" : "white"
                            border.color: "#dee2e6"
                            border.width: 1
                        }

                        contentItem: RowLayout {
                            spacing: 10

                            // File icon/type
                            Rectangle {
                                width: 40
                                height: 40
                                color: model.isGGUF ? "#27ae60" : "#95a5a6"
                                radius: 5

                                Label {
                                    anchors.centerIn: parent
                                    text: model.isGGUF ? "GGUF" : "FILE"
                                    color: "white"
                                    font.pixelSize: 9
                                    font.bold: true
                                }
                            }

                            // File info
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2

                                Label {
                                    text: model.filename
                                    font.pixelSize: 13
                                    font.bold: model.isGGUF
                                    Layout.fillWidth: true
                                    elide: Text.ElideMiddle
                                }

                                Label {
                                    text: model.size + (model.quantisation ? " • " + model.quantisation : "")
                                    font.pixelSize: 11
                                    color: "#7f8c8d"
                                }
                            }

                            // Download button
                            Button {
                                text: "⬇️ Download"
                                onClicked: {
                                    console.log("Download file:", model.filename)
                                }
                            }
                        }
                    }

                    ScrollBar.vertical: ScrollBar {}
                }
            }
        }

        // Licence
        GroupBox {
            Layout.fillWidth: true
            title: "Licence"
            visible: modelData !== null && modelData.licence

            Label {
                text: modelData ? modelData.licence : ""
                font.pixelSize: 13
            }
        }

        Item { Layout.fillHeight: true }
    }
}
