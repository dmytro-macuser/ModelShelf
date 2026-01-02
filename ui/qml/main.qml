import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1280
    height: 800
    visible: true
    title: "ModelShelf 🙂"

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

        // Main content area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#ecf0f1"

            StackLayout {
                anchors.fill: parent
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
                Discover {
                    id: discoverView
                }

                // Downloads view (placeholder)
                Item {
                    Label {
                        anchors.centerIn: parent
                        text: "Downloads\n\nComing in M2"
                        font.pixelSize: 18
                        color: "#95a5a6"
                        horizontalAlignment: Text.AlignHCenter
                    }
                }

                // Shelf view (placeholder)
                Item {
                    Label {
                        anchors.centerIn: parent
                        text: "Shelf\n\nComing in M3"
                        font.pixelSize: 18
                        color: "#95a5a6"
                        horizontalAlignment: Text.AlignHCenter
                    }
                }

                // Settings view (placeholder)
                Item {
                    Label {
                        anchors.centerIn: parent
                        text: "Settings\n\nComing in M4"
                        font.pixelSize: 18
                        color: "#95a5a6"
                        horizontalAlignment: Text.AlignHCenter
                    }
                }

                // About view (placeholder)
                Item {
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 10

                        Label {
                            text: "ModelShelf 🙂"
                            font.pixelSize: 24
                            font.bold: true
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Label {
                            text: "v0.1.0-dev (M1)"
                            font.pixelSize: 14
                            color: "#7f8c8d"
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Label {
                            text: "Download once. Organise forever."
                            font.pixelSize: 12
                            color: "#95a5a6"
                            Layout.alignment: Qt.AlignHCenter
                            Layout.topMargin: 10
                        }

                        Label {
                            text: "MIT Licence"
                            font.pixelSize: 10
                            color: "#95a5a6"
                            Layout.alignment: Qt.AlignHCenter
                            Layout.topMargin: 20
                        }
                    }
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
