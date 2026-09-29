"""Token minting for the mock PPG (docs/api-contracts.md section 1).

The real gateway validates credentials and keeps server-side sessions. The mock
accepts any `apiKey`/`secretKey` (docs/AGENTS.md section 8), so a token needs no
storage: it is random bytes, and validating one means checking that the client
sent a non-empty `Authorization: Bearer` header. Stateless also keeps this
module free of the dict that used to hold the purchases (see ADR-008).
"""

import secrets
from typing import Any


class TokenService:
    """Issues and refreshes PPG access/refresh token pairs."""

    def issue_token(self, api_key: str, secret_key: str) -> dict[str, Any]:
        """Return a fresh token pair, accepting any credentials.

        Args:
            api_key: Checked for presence only; any value is accepted.
            secret_key: Checked for presence only; any value is accepted.

        Returns:
            dict[str, Any]: `TokenResponse` fields.
        """
        return self._new_pair()

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Exchange a refresh token for a new pair.

        Any non-empty refresh token is accepted, for the same reason
        `issue_token` accepts any credentials.

        Args:
            refresh_token: The token being exchanged.

        Returns:
            dict[str, Any]: `TokenResponse` fields.
        """
        return self._new_pair()


    @staticmethod
    def _new_pair() -> dict[str, Any]:
        """Mint one random access/refresh pair.

        `token_hex` is used instead of a JWT: the merchant only ever passes the
        string back in a header, so a decodable structure would teach nothing.

        Returns:
            dict[str, Any]: `TokenResponse` fields.
        """
        return {
            "accessToken": secrets.token_hex(16),
            "refreshToken": secrets.token_hex(16),
            "tokenType": "Bearer",
            "expiresIn": 3600,
        }