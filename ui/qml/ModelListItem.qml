import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ItemDelegate {
    id: root
    property var modelData
    
    height: contentLayout.implicitHeight + 20
    
    background: Rectangle {
        color: root.hovered ? "#ecf0f1" : "white"
        radius: 5
        border.color: root.hovered ? "#3498db" : "#bdc3c7"
        border.width: 1
    }
    
    contentItem: RowLayout {
        id: contentLayout
        spacing: 10
        
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 5
            
            // Model name
            Label {
                text: modelData.name
                font.pixelSize: 14
                font.bold: true
                Layout.fillWidth: true
                elide: Text.ElideRight
            }
            
            // Author
            Label {
                text: "by " + modelData.author
                font.pixelSize: 12
                color: "#7f8c8d"
            }
            
            // Stats
            RowLayout {
                spacing: 15
                
                Label {
                    text: "⬇ " + modelData.downloads.toLocaleString()
                    font.pixelSize: 11
                    color: "#7f8c8d"
                }
                
                Label {
                    text: "❤ " + modelData.likes.toLocaleString()
                    font.pixelSize: 11
                    color: "#7f8c8d"
                }
                
                Label {
                    text: modelData.totalSize
                    font.pixelSize: 11
                    color: "#7f8c8d"
                }
            }
        }
        
        // GGUF badge
        Rectangle {
            visible: modelData.hasGguf
            color: "#27ae60"
            radius: 3
            width: ggufLabel.implicitWidth + 10
            height: ggufLabel.implicitHeight + 6
            
            Label {
                id: ggufLabel
                anchors.centerIn: parent
                text: "GGUF"
                color: "white"
                font.pixelSize: 10
                font.bold: true
            }
        }
    }
}
