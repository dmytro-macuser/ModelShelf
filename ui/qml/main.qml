import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

ApplicationWindow {
    id: root
    width: 1200
    height: 800
    visible: true
    title: "ModelShelf 🙂"

    // Navigation state
    property string currentView: "discover"

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
                    isActive: currentView === "discover"
                    onClicked: currentView = "discover"
                }

                NavButton {
                    text: "Downloads"
                    isActive: currentView === "downloads"
                    onClicked: currentView = "downloads"
                }

                NavButton {
                    text: "Shelf"
                    isActive: currentView === "shelf"
                    onClicked: currentView = "shelf"
                }

                Item {
                    Layout.fillHeight: true
                }

                NavButton {
                    text: "Settings"
                    isActive: currentView === "settings"
                    onClicked: currentView = "settings"
                }

                NavButton {
                    text: "About"
                    isActive: currentView === "about"
                    onClicked: currentView = "about"
                }
            }
        }

        // Main content area with view switching
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: {
                switch(currentView) {
                    case "discover": return 0
                    case "downloads": return 1
                    case "shelf": return 2
                    case "settings": return 3
                    case "about": return 4
                    default: return 0
                }
            }

            // Discover view
            DiscoverView {
                id: discoverView
            }

            // Downloads view (placeholder)
            PlaceholderView {
                viewName: "Downloads"
                description: "Download queue will appear here\n(Coming in M2)"
            }

            // Shelf view (placeholder)
            PlaceholderView {
                viewName: "Shelf"
                description: "Your local model library\n(Coming in M3)"
            }

            // Settings view (placeholder)
            PlaceholderView {
                viewName: "Settings"
                description: "Application settings\n(Coming in M4)"
            }

            // About view
            PlaceholderView {
                viewName: "About ModelShelf"
                description: "Version 0.1.0-dev\nM1: Hub Browsing\n\nDownload once. Organise forever."
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

    // Placeholder view component
    component PlaceholderView: Rectangle {
        property string viewName: "View"
        property string description: ""
        
        color: "#ecf0f1"

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 15

            Label {
                text: viewName
                font.pixelSize: 24
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                text: description
                font.pixelSize: 14
                color: "#7f8c8d"
                horizontalAlignment: Text.AlignHCenter
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }
}
