import XCTest
@testable import ios_search_ads_sample

final class AttributionResponseParserTests: XCTestCase {
    func testAcceptsStrictBooleanAttribution() throws {
        let response = makeResponse(statusCode: 200, contentType: "application/json; charset=utf-8")

        XCTAssertTrue(try AttributionResponseParser.parse(
            data: Data(#"{"attribution":true}"#.utf8),
            response: response,
            maximumResponseBytes: 1_024))
        XCTAssertFalse(try AttributionResponseParser.parse(
            data: Data(#"{"attribution":false}"#.utf8),
            response: response,
            maximumResponseBytes: 1_024))
    }

    func testRejectsNumericAndStringBooleanLookalikes() {
        for body in [#"{"attribution":1}"#, #"{"attribution":0}"#, #"{"attribution":"true"}"#] {
            XCTAssertThrowsError(try AttributionResponseParser.parse(
                data: Data(body.utf8),
                response: makeResponse(),
                maximumResponseBytes: 1_024)) { error in
                XCTAssertEqual(error as? AttributionClientError, .invalidPayload)
            }
        }
    }

    func testRejectsMalformedMissingAndTopLevelArrayPayloads() {
        for body in ["{", "{}", "[]", "null"] {
            XCTAssertThrowsError(try AttributionResponseParser.parse(
                data: Data(body.utf8),
                response: makeResponse(),
                maximumResponseBytes: 1_024)) { error in
                XCTAssertEqual(error as? AttributionClientError, .invalidPayload)
            }
        }
    }

    func testRejectsUnexpectedStatusMimeTypeAndOversizedBodies() {
        XCTAssertThrowsError(try AttributionResponseParser.parse(
            data: Data(#"{"attribution":true}"#.utf8),
            response: makeResponse(statusCode: 204),
            maximumResponseBytes: 1_024)) { error in
                XCTAssertEqual(error as? AttributionClientError, .unexpectedStatus(204))
            }
        XCTAssertThrowsError(try AttributionResponseParser.parse(
            data: Data(#"{"attribution":true}"#.utf8),
            response: makeResponse(contentType: "text/plain"),
            maximumResponseBytes: 1_024)) { error in
                XCTAssertEqual(error as? AttributionClientError, .invalidContentType)
            }
        XCTAssertThrowsError(try AttributionResponseParser.parse(
            data: Data(repeating: 0x20, count: 1_025),
            response: makeResponse(),
            maximumResponseBytes: 1_024)) { error in
                XCTAssertEqual(error as? AttributionClientError, .responseTooLarge)
            }
    }

    private func makeResponse(
        statusCode: Int = 200,
        contentType: String = "application/json"
    ) -> HTTPURLResponse {
        HTTPURLResponse(
            url: URL(string: "https://api-adservices.apple.com/api/v1/")!,
            statusCode: statusCode,
            httpVersion: "HTTP/1.1",
            headerFields: ["Content-Type": contentType])!
    }
}
