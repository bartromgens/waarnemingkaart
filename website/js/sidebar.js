
function updateFamilySpeciesPanel(family_slug) {
    $.get(
        "/bioclass/family/species/",
        {
            family_slug: family_slug,
        },
        function(data) {
            $("#family-species-sidebar-panel").html(data.html);
        },
        "json"
    );
}


module.exports = {
    updateFamilySpeciesPanel: updateFamilySpeciesPanel,
};
