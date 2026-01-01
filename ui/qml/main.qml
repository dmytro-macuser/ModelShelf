import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1200
    height: 800
    visible: true
    title: "ModelShelf 🙂"

    // Main layout
    RowLayout {
        anchors.fill: parent
        spacing: 0

        // Sidebar navigation
        Rectangle {
            Layout.preferredWidth: 200
            Layout.fillHeight: true
            color: "#2c3e50"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 5

                // Logo/Title
                Label {
                    text: "ModelShelf 🙂"
                    font.pixelSize: 18
                    font.bold: true
                    color: "white"
                    Layout.alignment: Qt.AlignHCenter
                    Layout.topMargin: 10
                    Layout.bottomMargin: 20
                }

                // Navigation buttons
                NavButton {
                    text: "Discover"
                    isActive: true
                }

                NavButton {
                    text: "Downloads"
                }

                NavButton {
                    text: "Shelf"
                }

                Item {
                    Layout.fillHeight: true
                }

                NavButton {
                    text: "Settings"
                }

                NavButton {
                    text: "About"
                }
            }
        }

        // Main content area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#ecf0f1"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20

                Label {
                    text: "Welcome to ModelShelf"
                    font.pixelSize: 24
                    font.bold: true
                }

                Label {
                    text: "Download once. Organise forever."
                    font.pixelSize: 14
                    color: "#7f8c8d"
                }

                Item {
                    Layout.fillHeight: true
                }

                Label {
                    text: "Skeleton UI loaded successfully (M0)"
                    font.pixelSize: 12
                    color: "#95a5a6"
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
    }

    // Navigation button component
    component NavButton: Button {
        property bool isActive: false
        
        Layout.fillWidth: true
        Layout.preferredHeight: 40
        
        background: Rectangle {
            color: parent.isActive ? "#34495e" : "transparent"
            radius: 5
        }
        
        contentItem: Label {
            text: parent.text
            color: "white"
            horizontalAlignment: Text.AlignLeft
            verticalAlignment: Text.AlignVCenter
            leftPadding: 10
        }
        
        hoverEnabled: true
        
        onHoveredChanged: {
            background.color = hovered ? "#34495e" : (isActive ? "#34495e" : "transparent")
        }
    }
}
