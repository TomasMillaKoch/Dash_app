window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            return L.circleMarker(feature.coordinates);
        }
    }
});