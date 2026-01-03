import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects
import ModelShelf 1.0

Item {
    id: root
    
    property bool loading: false
    
    // Shelf bridge
    ShelfBridge {
        id: shelfBridge
        
        onScanStarted: {
            loading = true
        }
        
        onScanCompleted: function(models, count, totalSize) {
            loading = false
            shelfModel.clear()
            for (var i = 0; i < models.length; i++) {
                shelfModel.append(models[i])
            }
            modelCount.text = count + " models"
            totalSizeLabel.text = totalSize
        }
        
        onModelDeleted: function(modelId) {
            for (var i = 0; i < shelfModel.count; i++) {
                if (shelfModel.get(i).id === modelId) {
                    shelfModel.remove(i)
                    break
                }
            }
            shelfBridge.scanLibrary(false)  // Refresh counts
        }
    }
    
    ListModel {
        id: shelfModel
    }
    
    Component.onCompleted: {
        shelfBridge.scanLibrary(false)
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15
        
        // Header
        RowLayout {
            Layout.fillWidth: true
            
            Label {
                text: "My Shelf"
                font.pixelSize: 24
                font.bold: true
            }
            
            Item { Layout.fillWidth: true }
            
            // Stats
            ColumnLayout {
                spacing: 2
                
                Label {
                    id: modelCount
                    text: "0 models"
                    font.pixelSize: 14
                    Layout.alignment: Qt.AlignRight
                }
                
                Label {
                    id: totalSizeLabel
                    text: "0 B"
                    font.pixelSize: 12
                    color: "#7f8c8d"
                    Layout.alignment: Qt.AlignRight
                }
            }
            
            Button {
                text: "⟳ Refresh"
                onClicked: shelfBridge.scanLibrary(true)
                enabled: !loading
            }
        }
        
        // Empty state
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: shelfModel.count === 0 && !loading
            
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 20
                
                // Empty bookshelf illustration
                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    width: 300
                    height: 200
                    color: "transparent"
                    
                    // Draw empty shelves
                    Column {
                        anchors.fill: parent
                        spacing: 20
                        
                        Repeater {
                            model: 3
                            
                            Rectangle {
                                width: 300
                                height: 8
                                color: "#8b7355"
                                radius: 2
                                
                                // Shadow
                                Rectangle {
                                    anchors.top: parent.bottom
                                    anchors.topMargin: 1
                                    width: parent.width
                                    height: 3
                                    color: "#00000020"
                                    radius: 2
                                }
                            }
                        }
                    }
                }
                
                Label {
                    text: "📚 Your shelf is empty"
                    font.pixelSize: 20
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Label {
                    text: "Download models from Discover to see them here"
                    font.pixelSize: 14
                    color: "#7f8c8d"
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
        
        // Loading state
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: loading
            
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 15
                
                BusyIndicator {
                    Layout.alignment: Qt.AlignHCenter
                    running: loading
                }
                
                Label {
                    text: "Scanning library..."
                    font.pixelSize: 14
                    color: "#7f8c8d"
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
        
        // Bookshelf view
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: shelfModel.count > 0 && !loading
            clip: true
            
            Column {
                width: parent.width
                spacing: 40
                
                // Create shelves (group books by rows)
                Repeater {
                    model: Math.ceil(shelfModel.count / 5)  // 5 books per shelf
                    
                    Item {
                        width: parent.width
                        height: 200
                        
                        // Shelf board
                        Rectangle {
                            anchors.bottom: parent.bottom
                            width: parent.width
                            height: 12
                            color: "#8b7355"
                            radius: 3
                            
                            // Wood grain effect
                            Rectangle {
                                anchors.fill: parent
                                color: "#00000010"
                                radius: parent.radius
                            }
                            
                            // Shadow
                            Rectangle {
                                anchors.top: parent.bottom
                                anchors.topMargin: 1
                                width: parent.width
                                height: 4
                                color: "#00000020"
                                radius: 3
                            }
                        }
                        
                        // Books on this shelf
                        Row {
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 12
                            anchors.horizontalCenter: parent.horizontalCenter
                            spacing: 15
                            
                            Repeater {
                                model: {
                                    var startIdx = index * 5
                                    var endIdx = Math.min(startIdx + 5, shelfModel.count)
                                    return endIdx - startIdx
                                }
                                
                                BookSpine {
                                    property int globalIndex: (parent.parent.parent.parent.parent.children[index] ? index * 5 : 0) + model.index
                                    modelData: globalIndex < shelfModel.count ? shelfModel.get(globalIndex) : null
                                    onClicked: {
                                        if (modelData) {
                                            detailsDialog.modelData = modelData
                                            detailsDialog.open()
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
    
    // Model details dialog
    Dialog {
        id: detailsDialog
        title: modelData ? modelData.name : ""
        width: 400
        height: 300
        anchors.centerIn: parent
        modal: true
        
        property var modelData: null
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 15
            
            Grid {
                columns: 2
                columnSpacing: 15
                rowSpacing: 8
                Layout.fillWidth: true
                
                Label { text: "Files:"; font.bold: true }
                Label { text: detailsDialog.modelData ? detailsDialog.modelData.fileCount : "" }
                
                Label { text: "GGUF Files:"; font.bold: true }
                Label { text: detailsDialog.modelData ? detailsDialog.modelData.ggufCount : "" }
                
                Label { text: "Total Size:"; font.bold: true }
                Label { text: detailsDialog.modelData ? detailsDialog.modelData.totalSize : "" }
                
                Label { text: "Location:"; font.bold: true }
                Label {
                    text: detailsDialog.modelData ? detailsDialog.modelData.path : ""
                    elide: Text.ElideMiddle
                    Layout.fillWidth: true
                }
            }
            
            Item { Layout.fillHeight: true }
            
            RowLayout {
                Layout.fillWidth: true
                
                Button {
                    text: "Open Folder"
                    icon.name: "folder-open"
                    onClicked: {
                        if (detailsDialog.modelData) {
                            shelfBridge.openFolder(detailsDialog.modelData.id)
                        }
                    }
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Delete"
                    icon.name: "delete"
                    onClicked: deleteConfirmDialog.open()
                }
            }
        }
    }
    
    // Delete confirmation dialog
    Dialog {
        id: deleteConfirmDialog
        title: "Delete Model?"
        width: 350
        anchors.centerIn: parent
        modal: true
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 15
            
            Label {
                text: "Are you sure you want to delete this model?\n\nThis will permanently delete all files."
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }
            
            RowLayout {
                Layout.fillWidth: true
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Cancel"
                    onClicked: deleteConfirmDialog.close()
                }
                
                Button {
                    text: "Delete"
                    highlighted: true
                    onClicked: {
                        if (detailsDialog.modelData) {
                            shelfBridge.deleteModel(detailsDialog.modelData.id)
                        }
                        deleteConfirmDialog.close()
                        detailsDialog.close()
                    }
                }
            }
        }
    }
}
