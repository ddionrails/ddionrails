import {SearchResult} from "@elastic/search-ui";
import {LanguageCode} from "../language_state";
import {resultFactoryMapper} from "../factory_mappers";

/**
 * Render header for variable result
 * @param result
 * @returns
 */
function header(result: SearchResult, onClickLink: () => void) {
  let title = result.title.snippet;
  if (typeof title === "undefined") {
    title = result.title.raw;
  }

  // eslint-disable-next-line require-jsdoc
  function setCursorCords(event: any) {
    document.body.style.setProperty("--x", String(event.pageX)+"px");
    document.body.style.setProperty("--y", String(event.pageY - window.scrollY)+"px");
  }

  let tooltipClass = "no-tooltip";
  const abstract = result.abstract.snippet;
  let abstractContainer = <></>;
  if (typeof abstract !== "undefined") {
    tooltipClass = "raw-tooltip";
    abstract.push("");
    abstractContainer = (
      <span
        className="raw-tooltiptext"
        dangerouslySetInnerHTML={{__html: abstract.join(" &hellip; ")}}
      ></span>
    );
  }
  return (
    <div className="header-subdivider">
      <h3>
        <i className="fa fa-newspaper"></i>
        <a
          onMouseOver={setCursorCords}
          onClick={onClickLink}
          href={"/publication/" + result._meta.id}
        >
          <span className={tooltipClass}>
            <span dangerouslySetInnerHTML={{__html: title}}></span>
            {abstractContainer}
          </span>
        </a>
      </h3>
    </div>
  );
}

/**
 * Render publication result body
 * @param result
 * @returns
 */
function publicationBody(result: SearchResult, language: LanguageCode) {
  let text = "Publication by";
  if (language === "de") {
    text = "Publikation von";
  }
  return (
    <p>
      {text} {result.author.raw} ({result.year.raw})
    </p>
  );
}

/**
 *
 * @param param0
 * @returns
 */
function publicationResultFactory({
  result,
  onClickLink,
  language,
}: {
  result: SearchResult;
  onClickLink: () => void;
  language: LanguageCode;
}) {
  return (
    <li className="sui-result">
      <div className="sui-result__header">{header(result, onClickLink)}</div>
      <div className="sui-result__body">
        {publicationBody(result, language)}
        <div className="sui-result__image">
          <img src={""} alt="" />
        </div>
        <div
          className="sui-result__details"
          dangerouslySetInnerHTML={{__html: result.description}}
        ></div>
      </div>
    </li>
  );
}

const publicationResult = resultFactoryMapper(publicationResultFactory);

export {publicationResult};
