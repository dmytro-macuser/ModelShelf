import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ModelShelf 1.0

Item {
    id: root
    
    // Search bridge
    SearchBridge {
        id: searchBridge
        
        onSearchCompleted: function(models, totalCount, hasNext) {
            searchInProgress = false
            modelListModel.clear()
            
            for (var i = 0; i < models.length; i++) {
                modelListModel.append(models[i])
            }
            
            resultCount.text = totalCount + " models found"
            nextButton.enabled = hasNext
        }
        
        onSearchFailed: function(error) {
            searchInProgress = false
            console.error("Search failed:", error)
            resultCount.text = "Search failed: " + error
        }
        
        onModelDetailsLoaded: function(details) {
            detailsPanel.modelDetails = details
            detailsPanel.visible = true
        }
        
        onModelDetailsLoadFailed: function(error) {
            console.error("Failed to load model details:", error)
        }
    }
    
    property bool searchInProgress: false
    property int currentPage: 0
    property int pageSize: 20
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15
        
        // Header
        Label {
            text: "Discover Models"
            font.pixelSize: 24
            font.bold: true
        }
        
        // Search bar
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            
            TextField {
                id: searchField
                Layout.fillWidth: true
                placeholderText: "Search models (e.g., 'llama', 'mistral')..."
                onAccepted: performSearch()
            }
            
            Button {
                text: "Search"
                enabled: !searchInProgress
                onClicked: performSearch()
            }
        }
        
        // Filters
        RowLayout {
            Layout.fillWidth: true
            spacing: 15
            
            CheckBox {
                id: ggufFilter
                text: "GGUF files only"
                checked: false
                onCheckedChanged: performSearch()
            }
            
            Label {
                text: "Sort by:"
            }
            
            ComboBox {
                id: sortCombo
                model: ["Downloads", "Likes", "Recent", "Trending"]
                currentIndex: 0
                onCurrentIndexChanged: performSearch()
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            Label {
                id: resultCount
                text: "0 models found"
                color: "#7f8c8d"
            }
        }
        
        // Results area
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10
            
            // Model list
            Rectangle {
                Layout.fillHeight: true
                Layout.preferredWidth: parent.width * 0.5
                border.color: "#bdc3c7"
                border.width: 1
                radius: 5
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 5
                    
                    ListView {
                        id: modelList
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        spacing: 5
                        
                        model: ListModel {
                            id: modelListModel
                        }
                        
                        delegate: ModelListItem {
                            width: modelList.width
                            modelData: model
                            onClicked: searchBridge.loadModelDetails(model.id)
                        }
                        
                        ScrollBar.vertical: ScrollBar {}
                        
                        Label {
                            anchors.centerIn: parent
                            text: searchInProgress ? "Searching..." : "No results\n\nTry searching for models"
                            color: "#95a5a6"
                            horizontalAlignment: Text.AlignHCenter
                            visible: modelList.count === 0
                        }
                    }
                    
                    // Pagination
                    RowLayout {
                        Layout.fillWidth: true
                        
                        Button {
                            id: prevButton
                            text: "Previous"
                            enabled: currentPage > 0 && !searchInProgress
                            onClicked: {
                                currentPage--
                                performSearch()
                            }
                        }
                        
                        Label {
                            Layout.fillWidth: true
                            text: "Page " + (currentPage + 1)
                            horizontalAlignment: Text.AlignHCenter
                        }
                        
                        Button {
                            id: nextButton
                            text: "Next"
                            enabled: false
                            onClicked: {
                                currentPage++
                                performSearch()
                            }
                        }
                    }
                }
            }
            
            // Details panel
            ModelDetailsPanel {
                id: detailsPanel
                Layout.fillHeight: true
                Layout.fillWidth: true
                visible: false
            }
        }
    }
    
    function performSearch() {
        if (searchInProgress) return
        
        searchInProgress = true
        currentPage = 0  // Reset to first page on new search
        
        var sortMap = ["downloads", "likes", "recent", "trending"]
        var sortBy = sortMap[sortCombo.currentIndex]
        
        searchBridge.search(
            searchField.text,
            ggufFilter.checked,
            sortBy,
            currentPage,
            pageSize
        )
    }
    
    Component.onCompleted: {
        // Perform initial search with popular models
        performSearch()
    }
}
