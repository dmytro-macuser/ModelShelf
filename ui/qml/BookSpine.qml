import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Book spine component for the shelf
Rectangle {
    id: root
    
    property var modelData: null
    signal clicked()
    
    width: 60 + (modelData ? Math.min(modelData.ggufCount * 10, 40) : 0)
    height: 150
    
    // Random-ish colors based on model ID hash
    property var bookColors: [
        "#3498db", "#e74c3c", "#2ecc71", "#f39c12",
        "#9b59b6", "#1abc9c", "#34495e", "#e67e22",
        "#c0392b", "#16a085", "#27ae60", "#2980b9"
    ]
    
    property int colorIndex: {
        if (!modelData || !modelData.id) return 0
        var hash = 0
        for (var i = 0; i < modelData.id.length; i++) {
            hash = ((hash << 5) - hash) + modelData.id.charCodeAt(i)
            hash = hash & hash
        }
        return Math.abs(hash) % bookColors.length
    }
    
    color: modelData ? bookColors[colorIndex] : "#95a5a6"
    radius: 2
    
    // Spine decoration
    border.width: 1
    border.color: Qt.darker(color, 1.2)
    
    // Book title on spine (vertical)
    Label {
        anchors.centerIn: parent
        width: parent.height - 20
        height: parent.width - 10
        rotation: -90
        transformOrigin: Item.Center
        
        text: modelData ? modelData.name : "..."
        color: "white"
        font.pixelSize: 11
        font.bold: true
        elide: Text.ElideRight
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        
        // Text shadow for readability
        style: Text.Outline
        styleColor: Qt.darker(root.color, 1.5)
    }
    
    // GGUF badge (small circle at bottom)
    Rectangle {
        visible: modelData && modelData.ggufCount > 0
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 10
        width: 20
        height: 20
        radius: 10
        color: "#27ae60"
        border.width: 2
        border.color: "white"
        
        Label {
            anchors.centerIn: parent
            text: modelData ? modelData.ggufCount : "0"
            color: "white"
            font.pixelSize: 10
            font.bold: true
        }
    }
    
    // Hover effect
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        
        onEntered: {
            root.scale = 1.05
            root.z = 10
        }
        
        onExited: {
            root.scale = 1.0
            root.z = 0
        }
        
        onClicked: root.clicked()
    }
    
    // Smooth scaling
    Behavior on scale {
        NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
    }
    
    // 3D-ish lighting effect
    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 3
        color: Qt.lighter(root.color, 1.3)
        radius: parent.radius
    }
    
    Rectangle {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 2
        color: Qt.darker(root.color, 1.4)
        radius: parent.radius
    }
}
