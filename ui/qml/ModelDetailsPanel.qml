import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ModelShelf 1.0

Rectangle {
    id: root
    border.color: "#bdc3c7"
    border.width: 1
    radius: 5
    color: "white"
    
    property var modelDetails: null
    
    // Create download bridge instance locally for this panel
    DownloadBridge {
        id: downloadBridge
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 15
        spacing: 10
        
        // Header
        RowLayout {
            Layout.fillWidth: true
            
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 5
                
                Label {
                    text: modelDetails ? modelDetails.name : "Model Details"
                    font.pixelSize: 18
                    font.bold: true
                    Layout.fillWidth: true
                    wrapMode: Text.Wrap
                }
                
                Label {
                    text: modelDetails ? "by " + modelDetails.author : ""
                    font.pixelSize: 12
                    color: "#7f8c8d"
                    visible: modelDetails !== null
                }
            }
            
            Button {
                text: "×"
                font.pixelSize: 20
                flat: true
                onClicked: root.visible = false
            }
        }
        
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            ColumnLayout {
                width: parent.width
                spacing: 15
                
                // Description
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5
                    visible: modelDetails !== null
                    
                    Label {
                        text: "Description"
                        font.bold: true
                        font.pixelSize: 14
                    }
                    
                    Label {
                        text: modelDetails ? modelDetails.description : ""
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                        color: "#2c3e50"
                    }
                }
                
                // Metadata
                Grid {
                    columns: 2
                    columnSpacing: 20
                    rowSpacing: 8
                    visible: modelDetails !== null
                    
                    Label { text: "Licence:"; font.bold: true }
                    Label { text: modelDetails ? modelDetails.licence : "" }
                    
                    Label { text: "Downloads:"; font.bold: true }
                    Label { text: modelDetails ? modelDetails.downloads.toLocaleString() : "" }
                    
                    Label { text: "Likes:"; font.bold: true }
                    Label { text: modelDetails ? modelDetails.likes.toLocaleString() : "" }
                    
                    Label { text: "Total Size:"; font.bold: true }
                    Label { text: modelDetails ? modelDetails.totalSize : "" }
                }
                
                // Tags
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5
                    visible: modelDetails && modelDetails.tags.length > 0
                    
                    Label {
                        text: "Tags"
                        font.bold: true
                        font.pixelSize: 14
                    }
                    
                    Flow {
                        Layout.fillWidth: true
                        spacing: 5
                        
                        Repeater {
                            model: modelDetails ? modelDetails.tags : []
                            
                            Rectangle {
                                color: "#ecf0f1"
                                radius: 3
                                width: tagLabel.implicitWidth + 12
                                height: tagLabel.implicitHeight + 8
                                
                                Label {
                                    id: tagLabel
                                    anchors.centerIn: parent
                                    text: modelData
                                    font.pixelSize: 11
                                    color: "#2c3e50"
                                }
                            }
                        }
                    }
                }
                
                // Files
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5
                    visible: modelDetails && modelDetails.files.length > 0
                    
                    Label {
                        text: "Files (" + (modelDetails ? modelDetails.files.length : 0) + ")"
                        font.bold: true
                        font.pixelSize: 14
                    }
                    
                    ListView {
                        Layout.fillWidth: true
                        Layout.preferredHeight: contentHeight
                        clip: true
                        spacing: 5
                        interactive: false
                        
                        model: modelDetails ? modelDetails.files : []
                        
                        delegate: Rectangle {
                            width: parent.width
                            height: fileLayout.implicitHeight + 12
                            color: modelData.isGguf ? "#e8f8f5" : "#f8f9fa"
                            border.color: modelData.isGguf ? "#27ae60" : "#dee2e6"
                            border.width: 1
                            radius: 3
                            
                            RowLayout {
                                id: fileLayout
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 10
                                
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2
                                    
                                    Label {
                                        text: modelData.filename
                                        font.pixelSize: 12
                                        font.bold: modelData.isGguf
                                        Layout.fillWidth: true
                                        elide: Text.ElideMiddle
                                    }
                                    
                                    RowLayout {
                                        spacing: 10
                                        
                                        Label {
                                            text: modelData.size
                                            font.pixelSize: 10
                                            color: "#7f8c8d"
                                        }
                                        
                                        Label {
                                            text: modelData.quantisation
                                            font.pixelSize: 10
                                            color: "#7f8c8d"
                                            visible: modelData.isGguf
                                        }
                                    }
                                }
                                
                                Button {
                                    text: "Download"
                                    onClicked: {
                                        // Trigger download via bridge
                                        downloadBridge.addDownload(
                                            modelDetails.id,
                                            modelData.filename,
                                            modelData.url,
                                            modelData.sizeBytes
                                        )
                                        // Provide feedback (could be improved)
                                        text = "Queued"
                                        enabled = false
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
