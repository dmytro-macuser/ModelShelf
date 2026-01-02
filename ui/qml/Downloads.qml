import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ModelShelf 1.0

Item {
    id: root
    
    // Download bridge
    DownloadBridge {
        id: downloadBridge
        
        onDownloadAdded: function(id) {
            refreshList()
        }
        
        onDownloadStateChanged: function(id, state) {
            for (var i = 0; i < downloadsModel.count; i++) {
                if (downloadsModel.get(i).id === id) {
                    downloadsModel.setProperty(i, "state", state)
                    break
                }
            }
        }
        
        onDownloadProgress: function(id, progress, speed, eta) {
            for (var i = 0; i < downloadsModel.count; i++) {
                if (downloadsModel.get(i).id === id) {
                    downloadsModel.setProperty(i, "progress", progress)
                    downloadsModel.setProperty(i, "speed", speed)
                    downloadsModel.setProperty(i, "eta", eta)
                    break
                }
            }
        }
    }
    
    ListModel {
        id: downloadsModel
    }
    
    function refreshList() {
        var items = downloadBridge.getDownloads()
        downloadsModel.clear()
        for (var i = 0; i < items.length; i++) {
            downloadsModel.append(items[i])
        }
    }
    
    Component.onCompleted: refreshList()
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15
        
        // Header
        RowLayout {
            Layout.fillWidth: true
            
            Label {
                text: "Downloads"
                font.pixelSize: 24
                font.bold: true
            }
            
            Item { Layout.fillWidth: true }
            
            Button {
                text: "Clear Completed"
                onClicked: {
                    // TODO: Implement clear completed
                }
            }
        }
        
        // Downloads List
        ListView {
            id: downloadList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 10
            
            model: downloadsModel
            
            delegate: Rectangle {
                width: downloadList.width
                height: 80
                color: "white"
                radius: 5
                border.color: "#bdc3c7"
                border.width: 1
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 15
                    
                    // Icon placeholder
                    Rectangle {
                        width: 50
                        height: 50
                        color: "#ecf0f1"
                        radius: 5
                        
                        Label {
                            anchors.centerIn: parent
                            text: "⬇"
                            font.pixelSize: 20
                        }
                    }
                    
                    // Info
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 5
                        
                        Label {
                            text: model.filename
                            font.bold: true
                            font.pixelSize: 14
                        }
                        
                        Label {
                            text: model.modelId
                            font.pixelSize: 12
                            color: "#7f8c8d"
                        }
                        
                        // Progress bar
                        ProgressBar {
                            Layout.fillWidth: true
                            value: model.progress
                            visible: model.state === "downloading" || model.state === "paused"
                        }
                        
                        // Status text
                        RowLayout {
                            visible: model.state === "downloading"
                            Label {
                                text: (model.progress * 100).toFixed(1) + "%"
                                font.pixelSize: 11
                            }
                            Label {
                                text: " • " + model.speed
                                font.pixelSize: 11
                                color: "#7f8c8d"
                            }
                            Label {
                                text: " • ETA: " + model.eta
                                font.pixelSize: 11
                                color: "#7f8c8d"
                            }
                        }
                        
                        Label {
                            visible: model.state !== "downloading"
                            text: {
                                switch(model.state) {
                                    case "queued": return "Queued"
                                    case "paused": return "Paused"
                                    case "completed": return "Completed"
                                    case "failed": return "Failed"
                                    case "cancelled": return "Cancelled"
                                    default: return model.state
                                }
                            }
                            font.pixelSize: 11
                            color: model.state === "completed" ? "#27ae60" : 
                                   model.state === "failed" ? "#c0392b" : "#7f8c8d"
                        }
                    }
                    
                    // Actions
                    RowLayout {
                        spacing: 5
                        
                        Button {
                            text: model.state === "paused" ? "Resume" : "Pause"
                            visible: model.state === "downloading" || model.state === "paused"
                            onClicked: {
                                if (model.state === "paused")
                                    downloadBridge.resumeDownload(model.id)
                                else
                                    downloadBridge.pauseDownload(model.id)
                            }
                        }
                        
                        Button {
                            text: "Retry"
                            visible: model.state === "failed" || model.state === "cancelled"
                            onClicked: downloadBridge.resumeDownload(model.id)
                        }
                        
                        Button {
                            text: "Cancel"
                            visible: model.state === "downloading" || model.state === "paused" || model.state === "queued"
                            onClicked: downloadBridge.cancelDownload(model.id)
                        }
                        
                        Button {
                            text: "Open"
                            visible: model.state === "completed"
                            onClicked: {
                                // TODO: Open folder
                            }
                        }
                    }
                }
            }
            
            Label {
                anchors.centerIn: parent
                text: "No downloads yet"
                color: "#95a5a6"
                visible: downloadsModel.count === 0
            }
        }
    }
}
