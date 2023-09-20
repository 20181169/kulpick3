import {AnyEditor} from "plugins/_lib2/AnyEditor";
import {DEFAULT_N1ED_CONF} from "_COMMON/configs";
import {AInstance} from "plugins/_lib2/instance/AInstance";
import {FeatureAmplitude} from "features/Amplitude/FeatureAmplitude";
import {FeatureTrial} from "features/Trial/FeatureTrial";
import {FeatureTrialDoubleCheck} from "features/TrialDoubleCheck/FeatureTrialDoubleCheck";
import {FeatureLocalStorage} from "features/LocalStorage/FeatureLocalStorage";
import {FeatureZIndexManager} from "features/ZIndexManager/FeatureZIndexManager";
import {FeatureN1EDLib} from "features/N1EDLib/FeatureN1EDLib";
import {FeatureCovers} from "features/Covers/FeatureCovers";
import {FeatureInclude} from "features/Include/FeatureInclude";
import {FeatureWidthPreview} from "features/WidthPreview/FeatureWidthPreview";
import {FeatureWaitForBootstrapEditor} from "features/WaitForBootstrapEditor/FeatureWaitForBootstrapEditor";
import {FeatureStructure} from "features/Structure/FeatureStructure";
import {FeatureBase64Buttons} from "features/Base64Buttons/FeatureBase64Buttons";
import {FeatureCKEditor} from "features/CKEditor/FeatureCKEditor";
import {FeatureTinyMCE} from "features/TinyMCE/FeatureTinyMCE";
import {FeatureMaximize} from "features/Maximize/FeatureMaximize";
import {FeatureLink} from "features/Link/Link";
import {FeatureCustomTemplates} from "features/CustomTemplates/FeatureCustomTemplates";
import {FeatureWidgets} from "features/Widgets/FeatureWidgets";
import {WidgetIgnored} from "features/Widgets/Ignored/WidgetIgnored";
import {WidgetAnchor} from "features/Widgets/Anchor/WidgetAnchor";
import {WidgetFontAwesome} from "features/Widgets/FontAwesome/WidgetFontAwesome";
import {WidgetImageGallery} from "features/Widgets/ImageGallery/WidgetImageGallery";
import {WidgetImageGalleryPreview} from "features/Widgets/ImageGallery/WidgetImageGalleryPreview";
import {WidgetImagePreview} from "features/Widgets/ImagePreview/WidgetImagePreview";
import {WidgetImage} from "features/Widgets/Image/WidgetImage";
import {WidgetBootstrapSection} from "features/Widgets/BootstrapContainer/WidgetBootstrapSection";
import {WidgetBootstrapContainerInsideSection} from "features/Widgets/BootstrapContainer/WidgetBootstrapContainerInsideSection";
import {WidgetBootstrapContainer} from "features/Widgets/BootstrapContainer/WidgetBootstrapContainer";
import {WidgetBootstrapRow} from "features/Widgets/BootstrapRow/WidgetBootstrapRow";
import {WidgetBootstrapCol} from "features/Widgets/BootstrapCol/WidgetBootstrapCol";
import {WidgetTable} from "features/Widgets/Table/WidgetTable";
import {WidgetTableRow} from "features/Widgets/TableRow/WidgetTableRow";
import {WidgetTableCol} from "features/Widgets/TableCol/WidgetTableCol";
import {WidgetTableCell} from "features/Widgets/TableCell/WidgetTableCell";
import {WidgetYouTube} from "features/Widgets/YouTube/WidgetYouTube";
import {WidgetIFrame} from "features/Widgets/IFrame/WidgetIFrame";
import {WidgetButton} from "features/Widgets/Link/WidgetButton";
import {WidgetLink} from "features/Widgets/Link/WidgetLink";
import {WidgetAlert} from "features/Widgets/Alert/WidgetAlert";
import {WidgetBadge} from "features/Widgets/Badge/WidgetBadge";
import {WidgetHTML} from "features/Widgets/HTML/WidgetHTML";
import {WidgetParagraph} from "features/Widgets/Paragraph/WidgetParagraph";
import {WidgetHeader} from "features/Widgets/Header/WidgetHeader";
import {WidgetAccordion} from "features/Widgets/Accordion/WidgetAccordion";
import {WidgetAccordionCard} from "features/Widgets/Accordion/WidgetAccordionCard";
import {WidgetAccordionCardHeader} from "features/Widgets/Accordion/WidgetAccordionCardHeader";
import {WidgetAccordionCardBody} from "features/Widgets/Accordion/WidgetAccordionCardBody";
import {WidgetBody} from "features/Widgets/Body/WidgetBody";
import {WidgetTag} from "features/Widgets/Tag/WidgetTag";
import {FeatureRemoveBreadcrumbsAndLogo} from "features/RemoveBreadcrumbsAndLogo/FeatureRemoveBreadcrumbsAndLogo";
import {FeatureLayoutClassic} from "features/LayoutClassic/FeatureLayoutClassic";
import {FeatureLayoutFullScreen} from "features/LayoutFullScreen/FeatureLayoutFullScreen";
import {FeatureRemovePlaceHolders} from "features/RemovePlaceHolders/FeatureRemovePlaceHolders";
import {WidgetTabs} from "features/Widgets/Tabs/WidgetTabs";
import {WidgetTabsContent} from "features/Widgets/Tabs/WidgetTabsContent";
import {WidgetTab} from "features/Widgets/Tabs/WidgetTab";
import {WidgetNav} from "features/Widgets/Tabs/WidgetNav";
import {WidgetNavItem} from "features/Widgets/Tabs/WidgetNavItem";
import {FeatureVersionInfo} from "features/VersionInfo/FeatureVersionInfo";
import {FeatureNotice} from "features/Notice/FeatureNotice";

function createFeaturesN1ED(instance: AInstance) {

    if (instance.getBooleanParameter("enableN1ED") === false)
        return [];

    return [
        new FeatureAmplitude(),
        new FeatureVersionInfo(),

        new FeatureNotice(),
        new FeatureTrial(),
        new FeatureTrialDoubleCheck(),

        new FeatureLocalStorage(),

        new FeatureZIndexManager(),

        new FeatureN1EDLib(),

        new FeatureCovers(),

        new FeatureInclude(),

        new FeatureWidthPreview(),

        new FeatureWaitForBootstrapEditor(),

        new FeatureStructure(),

        new FeatureBase64Buttons(),
        new FeatureCKEditor(),
        new FeatureTinyMCE(),

        new FeatureMaximize(),
        new FeatureLink(),

        new FeatureCustomTemplates(),
        new FeatureWidgets(
            // Widgets in order they need to check selected tags (from most prioritized)
            [
                new WidgetIgnored(),

                new WidgetAnchor(), // upper then Image to handle <img class="cke_anchor">
                new WidgetFontAwesome(), // upper then Image to handle <img class="fa-..."">

                new WidgetImageGallery(),
                new WidgetImageGalleryPreview(),
                new WidgetImagePreview(),
                new WidgetImage(),

                new WidgetBootstrapSection(),
                new WidgetBootstrapContainerInsideSection(),
                new WidgetBootstrapContainer(),
                new WidgetBootstrapRow(),
                new WidgetBootstrapCol(),

                new WidgetTable(),
                //new WidgetTableSection(), // ignored now
                new WidgetTableRow(),
                new WidgetTableCol(),
                new WidgetTableCell(),

                new WidgetAccordion(),
                new WidgetAccordionCard(),
                new WidgetAccordionCardHeader(),
                new WidgetAccordionCardBody(),

                new WidgetTabs(),
                new WidgetTabsContent(),
                new WidgetTab(),
                new WidgetNav(),
                new WidgetNavItem(),

                new WidgetYouTube(),
                new WidgetIFrame(),
                new WidgetButton(),
                new WidgetLink(),
                new WidgetAlert(),
                new WidgetBadge(),
                new WidgetHTML(),
                new WidgetParagraph(),
                new WidgetHeader(),

                new WidgetBody(),
                new WidgetTag()
            ]
        ),

        new FeatureRemoveBreadcrumbsAndLogo(),
        new FeatureLayoutClassic(),
        new FeatureLayoutFullScreen(),

        new FeatureRemovePlaceHolders()
    ]
}

AnyEditor.getEditor().addPlugin(
    {
        name: "N1ED",
        configDefaults: DEFAULT_N1ED_CONF,
        createFeatures: createFeaturesN1ED
    }
);